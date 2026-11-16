"""Customs rule sets, loaded from a data file (default: app/customs/tax_rates.json).

All tax numbers live in that JSON file, not in code. Each rule set lists the legal sources it is
based on; `scripts/check_law_updates.py` watches those sources and reports when the law text changes,
so a human can review and update the file (rates are never changed automatically).

Set TAX_RATES_PATH to load another file (e.g. one mounted from S3) without a redeploy.
"""
import json
import os
from dataclasses import dataclass
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
    notes: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class TaxRates:
    version: str
    verified_at: date
    parcel: dict[str, ParcelRules]
    car: dict[str, CarRules]
    sources: dict[str, dict]


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
        notes=tuple(r.get("notes", [])),
        sources=tuple(r.get("sources", [])),
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
    )
    for rule in (*rates.parcel.values(), *rates.car.values()):
        missing = [s for s in rule.sources if s not in rates.sources]
        if missing:
            raise ValueError(f"rule set '{rule.key}' references unknown sources: {missing}")
    for required in ("current", "july_2027"):
        if required not in rates.parcel:
            raise ValueError(f"parcel_rule_sets must contain '{required}'")
    if "current" not in rates.car:
        raise ValueError("car_rule_sets must contain 'current'")
    return rates


TAX_RATES = load_tax_rates()
PARCEL_RULES: dict[str, ParcelRules] = TAX_RATES.parcel
PARCEL_CURRENT = PARCEL_RULES["current"]
PARCEL_JULY_2027 = PARCEL_RULES["july_2027"]
CAR_CURRENT = TAX_RATES.car["current"]
