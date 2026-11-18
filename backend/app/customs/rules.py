"""Customs rule sets, loaded from a data file (default: app/customs/tax_rates.json).

All tax numbers live in that JSON file, not in code. Each rule set lists the legal sources it is
based on; `scripts/check_law_updates.py` watches those sources and reports when the law text changes,
so a human can review and update the file (rates are never changed automatically).

Set TAX_RATES_PATH to load another file (e.g. one mounted from S3) without a redeploy.
"""
import json
import os
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

DEFAULT_RATES_PATH = Path(__file__).with_name("tax_rates.json")


def _d(value) -> Decimal:
    return Decimal(str(value))


@dataclass(frozen=True)
class ParcelRules:
    key: str
    title: str
    duty_free_threshold_eur: Decimal  # above this: duty + VAT on the part above it (CC art. 374 p.7)
    duty_rate: Decimal
    vat_rate: Decimal
    vat_on_low_value: bool  # July 2027: VAT on the whole value of parcels <= threshold (no duty)
    private_exempt_up_to_eur: Decimal | None  # July 2027: P2P non-commercial parcels up to this stay tax-free
    simplified_limit_eur: Decimal  # above this: full commercial customs declaration (CC art. 374 p.8)
    # Base for duty and VAT on parcels above the threshold: "excess" (part above it; today, CC 374 p.7 + TC 191.1.1)
    # or "full_value" (whole invoice value; July 2027, Law 5026-IX item 19 + Law 5025-IX item 6)
    above_threshold_base: str = "excess"
    notes: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExciseBase:
    up_to_cc: int
    small: Decimal  # EUR per 1000 cm3 for engines <= up_to_cc
    large: Decimal  # EUR per 1000 cm3 for engines > up_to_cc

    def rate_for(self, cc: int) -> Decimal:
        return self.small if cc <= self.up_to_cc else self.large


@dataclass(frozen=True)
class DutyException:
    """A reduced duty rate for some cars (Customs Tariff), e.g. 5% for new petrol cars over 3000 cm3."""
    engine_types: tuple[str, ...]
    only_new: bool
    engine_cc_over: int
    rate: Decimal
    label: str

    def matches(self, engine_type: str, engine_cc: int | None, is_new: bool) -> bool:
        return (engine_type in self.engine_types and (is_new or not self.only_new)
                and engine_cc is not None and engine_cc > self.engine_cc_over)


@dataclass(frozen=True)
class CarRules:
    key: str
    title: str
    duty_rate_eu: Decimal
    duty_rate_other: Decimal
    electric_duty_rate: Decimal
    vat_rate: Decimal
    excise_base: dict[str, ExciseBase]  # "petrol" | "diesel"
    hybrid_excise_as: str  # hybrids pay excise by their combustion engine (TC 215.3.5-1)
    electric_eur_per_kwh: Decimal
    # K_age = full calendar years from the year AFTER manufacture to the current year, clamped
    age_coef_min: int
    age_coef_max: int
    duty_exceptions: tuple[DutyException, ...] = ()  # apply to non-EU-origin, non-electric cars
    notes: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()


RATE_BASES = ("litre", "litre_abs_alcohol", "1000_pcs", "kg", "1000_litres", "percent")
UNITS = ("l", "ml", "pcs", "g")


@dataclass(frozen=True)
class ExciseRate:
    """One duty or excise component of an excise good.

    per: what the rate is multiplied by — litres, litres of 100% alcohol, thousands of pieces, kg net,
    thousands of litres, or "percent" of the customs value. Values may change per calendar year (by_year).
    """
    per: str
    currency: str | None  # "EUR" | "UAH"; None for percent
    by_year: dict[int, Decimal]  # a single value is stored under year 0 (valid every year)
    ad_valorem: Decimal | None = None  # cigarettes: + this share of the price ...
    minimum_by_year: dict[int, Decimal] | None = None  # ... but not less than this per 1000 pcs

    @staticmethod
    def _pick(table: dict[int, Decimal], year: int) -> tuple[Decimal, int]:
        if 0 in table:
            return table[0], year
        known = sorted(table)
        y = year if year in table else (known[-1] if year > known[-1] else known[0])
        return table[y], y

    def value(self, year: int) -> tuple[Decimal, int]:
        """(rate, year the rate belongs to) — the latest known year is used after the schedule ends."""
        return self._pick(self.by_year, year)

    def minimum(self, year: int) -> Decimal | None:
        return self._pick(self.minimum_by_year, year)[0] if self.minimum_by_year else None


@dataclass(frozen=True)
class ExciseKind:
    key: str
    label: str
    group: str  # alcohol | tobacco | e_liquid | fuel
    unit: str  # l | ml | pcs | g
    allowance: Decimal  # duty-free quantity per adult in luggage (in `unit`)
    allowance_note: str
    duty: ExciseRate
    excise: ExciseRate
    abv_required: bool = False
    abv_default: Decimal | None = None
    abv_min: Decimal | None = None
    abv_max: Decimal | None = None
    weight_required: bool = False


@dataclass(frozen=True)
class ExciseRules:
    key: str
    title: str
    vat_rate: Decimal
    allowance_groups_24h: tuple[str, ...]  # groups whose allowance is void after < 24 h abroad (MK 376 p.3)
    kinds: dict[str, ExciseKind]
    notes: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaxRates:
    version: str
    verified_at: date
    parcel: dict[str, ParcelRules]
    car: dict[str, CarRules]
    sources: dict[str, dict]
    excise: dict[str, ExciseRules] = field(default_factory=dict)


def _base(value: str) -> str:
    if value not in ("excess", "full_value"):
        raise ValueError(f"above_threshold_base must be 'excess' or 'full_value', got {value!r}")
    return value


def _parcel(key: str, r: dict) -> ParcelRules:
    exempt = r.get("private_exempt_up_to_eur")
    return ParcelRules(
        key=key,
        title=r["title"],
        duty_free_threshold_eur=_d(r["duty_free_threshold_eur"]),
        duty_rate=_d(r["duty_rate"]),
        vat_rate=_d(r["vat_rate"]),
        vat_on_low_value=bool(r["vat_on_low_value"]),
        private_exempt_up_to_eur=_d(exempt) if exempt is not None else None,
        simplified_limit_eur=_d(r["simplified_limit_eur"]),
        above_threshold_base=_base(r.get("above_threshold_base", "excess")),
        notes=tuple(r.get("notes", [])),
        sources=tuple(r.get("sources", [])),
    )


def _car(key: str, r: dict) -> CarRules:
    excise = {
        fuel: ExciseBase(up_to_cc=int(v["up_to_cc"]), small=_d(v["small"]), large=_d(v["large"]))
        for fuel, v in r["excise_base_eur"].items()
    }
    if r["hybrid_excise_as"] not in excise:
        raise ValueError(f"hybrid_excise_as must be one of {sorted(excise)}")
    return CarRules(
        key=key,
        title=r["title"],
        duty_rate_eu=_d(r["duty_rate_eu"]),
        duty_rate_other=_d(r["duty_rate_other"]),
        electric_duty_rate=_d(r["electric_duty_rate"]),
        vat_rate=_d(r["vat_rate"]),
        excise_base=excise,
        hybrid_excise_as=r["hybrid_excise_as"],
        electric_eur_per_kwh=_d(r["electric_eur_per_kwh"]),
        age_coef_min=int(r["age_coef_min"]),
        age_coef_max=int(r["age_coef_max"]),
        duty_exceptions=tuple(
            DutyException(
                engine_types=tuple(e["engine_types"]), only_new=bool(e["only_new"]),
                engine_cc_over=int(e["engine_cc_over"]), rate=_d(e["rate"]), label=e["label"],
            )
            for e in r.get("duty_exceptions", [])
        ),
        notes=tuple(r.get("notes", [])),
        sources=tuple(r.get("sources", [])),
    )


def _rate(r: dict) -> ExciseRate:
    if r["per"] not in RATE_BASES:
        raise ValueError(f"excise rate 'per' must be one of {RATE_BASES}, got {r['per']!r}")
    if ("value" in r) == ("by_year" in r):
        raise ValueError("an excise rate needs exactly one of 'value' or 'by_year'")
    by_year = {0: _d(r["value"])} if "value" in r else {int(y): _d(v) for y, v in r["by_year"].items()}
    minimum = {int(y): _d(v) for y, v in r["minimum_by_year"].items()} if "minimum_by_year" in r else None
    currency = r.get("currency")
    if r["per"] != "percent" and currency not in ("EUR", "UAH"):
        raise ValueError(f"excise rate per {r['per']} needs currency EUR or UAH")
    return ExciseRate(per=r["per"], currency=currency, by_year=by_year,
                      ad_valorem=_d(r["ad_valorem"]) if "ad_valorem" in r else None, minimum_by_year=minimum)


def _excise(key: str, r: dict) -> ExciseRules:
    kinds = {}
    for k, v in r["kinds"].items():
        if v["unit"] not in UNITS:
            raise ValueError(f"excise kind {k}: unit must be one of {UNITS}")
        abv = v.get("abv") or {}
        kinds[k] = ExciseKind(
            key=k, label=v["label"], group=v["group"], unit=v["unit"], allowance=_d(v["allowance"]),
            allowance_note=v["allowance_note"], duty=_rate(v["duty"]), excise=_rate(v["excise"]),
            abv_required=bool(abv.get("required", False)),
            abv_default=_d(abv["default"]) if "default" in abv else None,
            abv_min=_d(abv["min"]) if "min" in abv else None,
            abv_max=_d(abv["max"]) if "max" in abv else None,
            weight_required=bool(v.get("weight_required", False)),
        )
        if (kinds[k].excise.per == "litre_abs_alcohol" or kinds[k].duty.per == "litre_abs_alcohol") and not kinds[k].abv_required:
            raise ValueError(f"excise kind {k}: a rate per litre of 100% alcohol needs 'abv'")
        if "kg" in (kinds[k].duty.per, kinds[k].excise.per) and v["unit"] != "g" and not kinds[k].weight_required:
            raise ValueError(f"excise kind {k}: a rate per kg needs unit 'g' or weight_required")
    return ExciseRules(
        key=key, title=r["title"], vat_rate=_d(r["vat_rate"]),
        allowance_groups_24h=tuple(r.get("allowance_groups_24h", [])), kinds=kinds,
        notes=tuple(r.get("notes", [])), sources=tuple(r.get("sources", [])),
    )


def load_tax_rates(path: str | Path | None = None) -> TaxRates:
    """Load and validate the rates file. Fails loudly (at startup) on a broken file."""
    path = Path(path or os.environ.get("TAX_RATES_PATH") or DEFAULT_RATES_PATH)
    raw = json.loads(path.read_text(encoding="utf-8"))
    rates = TaxRates(
        version=raw["version"],
        verified_at=date.fromisoformat(raw["verified_at"]),
        parcel={k: _parcel(k, v) for k, v in raw["parcel_rule_sets"].items()},
        car={k: _car(k, v) for k, v in raw["car_rule_sets"].items()},
        sources=raw.get("sources", {}),
        excise={k: _excise(k, v) for k, v in raw.get("excise_rule_sets", {}).items()},
    )
    for rule in (*rates.parcel.values(), *rates.car.values(), *rates.excise.values()):
        missing = [s for s in rule.sources if s not in rates.sources]
        if missing:
            raise ValueError(f"rule set '{rule.key}' references unknown sources: {missing}")
    for required in ("current", "july_2027"):
        if required not in rates.parcel:
            raise ValueError(f"parcel_rule_sets must contain '{required}'")
    if "current" not in rates.car:
        raise ValueError("car_rule_sets must contain 'current'")
    if "current" not in rates.excise:
        raise ValueError("excise_rule_sets must contain 'current'")
    return rates


TAX_RATES = load_tax_rates()
PARCEL_RULES: dict[str, ParcelRules] = TAX_RATES.parcel
PARCEL_CURRENT = PARCEL_RULES["current"]
PARCEL_JULY_2027 = PARCEL_RULES["july_2027"]
CAR_CURRENT = TAX_RATES.car["current"]
EXCISE_CURRENT = TAX_RATES.excise["current"]
