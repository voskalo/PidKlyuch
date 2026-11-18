"""Customs calculators (Strategy pattern): one class per delivery type.

Each calculator is pure: input value object + rule set -> Breakdown (EUR).
Currency conversion and persistence are handled outside, in services.
"""
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from app.customs.models import (
    Breakdown, CarInput, EngineType, ExciseInput, Origin, ParcelInput, Sender, ShippedFrom, TaxLine, money,
)
from app.customs.rules import (
    CAR_CURRENT, EXCISE_CURRENT, PARCEL_CURRENT, CarRules, ExciseKind, ExciseRate, ExciseRules, ParcelRules,
)

ZERO = Decimal("0")


def _pct(rate: Decimal) -> str:
    return f"{(rate * 100).normalize():f}%"


class CustomsCalculator(ABC):
    @abstractmethod
    def calculate(self, data) -> Breakdown: ...


class ParcelCalculator(CustomsCalculator):
    def __init__(self, rules: ParcelRules = PARCEL_CURRENT):
        self.rules = rules

    def calculate(self, data: ParcelInput) -> Breakdown:
        r = self.rules
        goods = money(data.goods_value_eur)
        shipping = money(data.shipping_eur)
        threshold = money(r.duty_free_threshold_eur)
        result = Breakdown(rules_key=r.key, goods_value_eur=goods, shipping_eur=shipping, notes=list(r.notes))

        if goods > r.simplified_limit_eur:
            result.notes.insert(0, (
                f"Вартість понад €{money(r.simplified_limit_eur)}: потрібне повне митне оформлення "
                "як для підприємств за повними ставками Митного тарифу — розрахунок орієнтовний."
            ))

        if goods > threshold:
            # Today (CC 374 p.7 + TC 191.1.1): duty on the part above the threshold, VAT on (that part + duty).
            # July 2027 (Law 5026-IX item 19 + Law 5025-IX item 6): both on the FULL invoice value.
            if r.above_threshold_base == "excess":
                base, base_label = goods - threshold, f"({goods} − {threshold})"
            else:
                base, base_label = goods, f"{goods}"
            duty = money(base * r.duty_rate)
            vat = money((base + duty) * r.vat_rate)
            result.lines.append(TaxLine(
                "duty", "Мито", duty, f"{_pct(r.duty_rate)} × {base_label} = {duty} EUR",
            ))
            result.lines.append(TaxLine(
                "vat", "ПДВ", vat, f"{_pct(r.vat_rate)} × ({money(base)} + {duty}) = {vat} EUR",
            ))
        elif r.vat_on_low_value:
            exempt = r.private_exempt_up_to_eur
            if data.sender is Sender.PRIVATE and exempt is not None and goods <= exempt:
                result.notes.insert(0, f"Некомерційна посилка від фізособи до €{money(exempt)}: податків немає.")
            elif goods > 0:
                vat = money(goods * r.vat_rate)
                result.lines.append(TaxLine(
                    "vat", "ПДВ", vat, f"{_pct(r.vat_rate)} × {goods} = {vat} EUR",
                ))
        else:
            result.notes.insert(0, f"Вартість товару не перевищує €{threshold}: податків немає.")
        return result


class ImportBanned(ValueError):
    """The goods may not be imported at all (e.g. shipped from or through russia, Cabinet resolution 426)."""


class CarCalculator(CustomsCalculator):
    def __init__(self, rules: CarRules = CAR_CURRENT, current_year: int | None = None, today: date | None = None):
        self.rules = rules
        self.today = today or (date(current_year, 12, 31) if current_year else date.today())
        self.current_year = current_year or self.today.year

    def age_coefficient(self, manufacture_year: int) -> int:
        """Full calendar years from the year after manufacture to the current year (TC 215.3.5-1)."""
        full_years = self.current_year - manufacture_year - 1
        return max(self.rules.age_coef_min, min(self.rules.age_coef_max, full_years))

    def is_new(self, data: CarInput) -> bool:
        """'New' as in the Customs Tariff (not used before). If the user did not say, assume a car
        made this year or later is new."""
        return data.is_new if data.is_new is not None else data.manufacture_year >= self.current_year

    def _normal_rate(self, data: CarInput) -> tuple[Decimal, str]:
        """Normal ("пільгова", WTO / most-favoured-nation) rate of the car's tariff line."""
        for exc in self.rules.duty_exceptions:
            if exc.matches(data.engine_type.value, data.engine_volume_cc, self.is_new(data)):
                return exc.rate, exc.label
        return self.rules.duty_rate_other, "звичайна ставка"

    def _duty_rate(self, data: CarInput) -> tuple[Decimal, str, list[str]]:
        """Duty rate by country of ORIGIN, corrected by country of DISPATCH (MK 36, 46, 280; free-trade agreements)."""
        r = self.rules
        if data.shipped_from is ShippedFrom.RUSSIA:
            raise ImportBanned("import of goods shipped from or through russia is banned (Cabinet resolution 426)")
        if data.engine_type is EngineType.ELECTRIC:
            return r.electric_duty_rate, "електромобіль: 0% за будь-якого походження", []
        if data.origin is Origin.UNPROVEN:
            return r.duty_rate_full, "походження не підтверджено — повна ставка", [
                "Походження не підтверджене — повна ставка мита (ст. 46 ч. 2 МКУ). Якщо протягом 1095 днів подати "
                "документ про походження, різницю можна повернути (ст. 46 ч. 4 МКУ)."]
        normal, normal_label = self._normal_rate(data)
        if data.origin is Origin.OTHER:
            return normal, normal_label, []
        pref = r.preferential_origins[data.origin.value]
        if data.shipped_from is ShippedFrom.OTHER:
            return normal, f"{normal_label}; пільгу втрачено", [
                f"Авто походженням з {pref.label}, але відправлене з іншої країни: пільга за угодою не діє "
                "(правило прямого транспортування, документ про походження видає експортер країни-партнера) — звичайна ставка."]
        if self.today < pref.valid_from:
            return normal, normal_label, [f"Пільгова ставка для {pref.label} діє з {pref.valid_from:%d.%m.%Y} — до того звичайна ставка."]
        notes = [f"Пільга: {pref.agreement}; потрібен документ про походження ({pref.proof}). Без нього — звичайна ставка."]
        if pref.valid_to and self.today > pref.valid_to:
            notes.append(f"Ставку для {pref.label} затверджено до {pref.valid_to:%d.%m.%Y}; на {self.today.year} рік її треба перевірити.")
        rate = pref.rate_for(normal)
        return rate, f"походження: {pref.label}", notes

    def _excise(self, data: CarInput) -> tuple[Decimal, str]:
        r = self.rules
        if data.engine_type is EngineType.ELECTRIC:
            if data.battery_kwh is None:
                raise ValueError("battery_kwh is required for electric cars")
            amount = money(r.electric_eur_per_kwh * Decimal(data.battery_kwh))
            return amount, f"{r.electric_eur_per_kwh} € × {data.battery_kwh} кВт·год = {amount} EUR"

        if not data.engine_volume_cc:
            raise ValueError("engine_volume_cc is required for petrol/diesel/hybrid cars")
        fuel = r.hybrid_excise_as if data.engine_type is EngineType.HYBRID else data.engine_type.value
        cc = data.engine_volume_cc
        rate = r.excise_base[fuel].rate_for(cc)
        litres = Decimal(cc) / Decimal(1000)
        by_year = self.age_coefficient(data.manufacture_year)
        # TC 215.3.5-1: "для нових транспортних засобів ... коефіцієнт дорівнює 1", whatever the manufacture year
        is_new = self.is_new(data)
        coef = r.age_coef_min if is_new else by_year
        coef_label = "коеф. віку, нове авто" if is_new and by_year != coef else "коеф. віку"
        amount = money(rate * litres * coef)
        return amount, f"{rate} € × {litres.normalize():f} л × {coef} ({coef_label}) = {amount} EUR"

    def calculate(self, data: CarInput) -> Breakdown:
        r = self.rules
        price = money(data.car_price_eur)
        shipping = money(data.shipping_eur)
        customs_value = price + shipping
        result = Breakdown(rules_key=r.key, goods_value_eur=price, shipping_eur=shipping, notes=list(r.notes))

        duty_rate, duty_label, duty_notes = self._duty_rate(data)
        result.notes[:0] = duty_notes
        duty = money(customs_value * duty_rate)
        result.lines.append(TaxLine(
            "duty", "Мито", duty, f"{_pct(duty_rate)} × {customs_value} ({duty_label}) = {duty} EUR",
        ))

        excise, excise_formula = self._excise(data)
        result.lines.append(TaxLine("excise", "Акциз", excise, excise_formula))

        vat = money((customs_value + duty + excise) * r.vat_rate)
        result.lines.append(TaxLine(
            "vat", "ПДВ", vat, f"{_pct(r.vat_rate)} × ({customs_value} + {duty} + {excise}) = {vat} EUR",
        ))
        return result


UNIT_LABEL = {"l": "л", "ml": "мл", "pcs": "шт", "g": "г"}


def _num(value: Decimal) -> str:
    """Decimal for formulas without trailing zeros: 1.500 -> 1.5, 200 -> 200."""
    return f"{value.normalize():f}"


class ExciseCalculator(CustomsCalculator):
    """Excise goods in luggage (MK 376, 374 p.10 / TC 215.3, transitional subsection 5).

    Above the duty-free allowance: duty (Customs Tariff, preferential column) + excise (Tax Code) +
    VAT 20% on (value + duty + excise), from the first euro — there is no €150/€500 threshold for excise goods.
    Only the quantity above the allowance is taxed; its value is the price share of that quantity.
    UAH-denominated excise rates are converted at the NBU EUR rate (eur_uah).
    """

    def __init__(self, rules: ExciseRules = EXCISE_CURRENT, eur_uah: Decimal = Decimal("50"),
                 current_year: int | None = None):
        if eur_uah <= 0:
            raise ValueError("eur_uah must be positive")
        self.rules = rules
        self.eur_uah = eur_uah
        self.year = current_year or date.today().year

    def allowance(self, kind: ExciseKind, under_24h: bool) -> Decimal:
        if under_24h and kind.group in self.rules.allowance_groups_24h:
            return ZERO
        return kind.allowance

    def _base(self, per: str, kind: ExciseKind, qty: Decimal, weight_kg: Decimal | None,
              abv: Decimal | None) -> tuple[Decimal, str]:
        """How many 'units of the rate' the taxed quantity is, plus a label for the formula."""
        litres = qty / 1000 if kind.unit == "ml" else qty
        if per == "litre":
            return litres, f"{_num(litres)} л"
        if per == "litre_abs_alcohol":
            return litres * abv / 100, f"{_num(litres)} л × {_num(abv)}%"
        if per == "1000_pcs":
            return qty / 1000, f"{_num(qty / 1000)} тис. шт"
        if per == "1000_litres":
            return litres / 1000, f"{_num(litres / 1000)} тис. л"
        if per == "kg":
            return weight_kg, f"{_num(weight_kg)} кг"
        raise ValueError(f"unsupported rate base {per!r}")

    def _component(self, rate: ExciseRate, kind: ExciseKind, qty: Decimal, value: Decimal,
                   weight_kg: Decimal | None, abv: Decimal | None) -> tuple[Decimal, str, int]:
        r, year = rate.value(self.year)
        if rate.per == "percent":
            amount = money(value * r)
            return amount, f"{_pct(r)} × {value} = {amount} EUR", year
        base, base_label = self._base(rate.per, kind, qty, weight_kg, abv)
        to_eur = (lambda x: x / self.eur_uah) if rate.currency == "UAH" else (lambda x: x)
        sym = "грн" if rate.currency == "UAH" else "€"
        conv = f" ÷ {_num(self.eur_uah)} грн/€" if rate.currency == "UAH" else ""
        specific = to_eur(r * base)
        if rate.ad_valorem is None:
            amount = money(specific)
            return amount, f"{_num(r)} {sym} × {base_label}{conv} = {amount} EUR", year
        # cigarettes: specific + ad valorem share of the price, but not less than the minimum (per 1000 pcs)
        minimum = to_eur(rate.minimum(self.year) * base)
        combined = specific + value * rate.ad_valorem
        amount = money(max(combined, minimum))
        return amount, (f"max({_num(r)} € × {base_label} + {_pct(rate.ad_valorem)} × {value}; "
                        f"мін. {_num(rate.minimum(self.year))} € × {base_label}) = {amount} EUR"), year

    def calculate(self, data: ExciseInput) -> Breakdown:
        kind = self.rules.kinds.get(data.kind)
        if kind is None:
            raise ValueError(f"unknown excise kind {data.kind!r}")
        if data.quantity <= 0:
            raise ValueError("quantity must be positive")
        abv = data.abv if data.abv is not None else kind.abv_default
        if kind.abv_required and abv is None:
            raise ValueError(f"abv is required for {data.kind}")
        if kind.weight_required and not data.weight_g:
            raise ValueError(f"weight_g is required for {data.kind}")

        price = money(data.price_eur)
        unit = UNIT_LABEL[kind.unit]
        result = Breakdown(rules_key=self.rules.key, goods_value_eur=price, shipping_eur=ZERO, notes=list(self.rules.notes))
        allowance = self.allowance(kind, data.under_24h)
        taxed_qty = max(ZERO, data.quantity - allowance)
        lost = data.under_24h and kind.allowance > 0 and allowance == 0
        result.notes.insert(0, (
            f"Безмитна норма на 1 особу від 18 років: {kind.allowance_note}."
            + (" Ви були за кордоном менше 24 годин — норма не діє (ст. 376 ч. 3 МКУ)." if lost else "")
        ))
        if taxed_qty == 0:
            result.notes.insert(0, f"{_num(data.quantity)} {unit} — у межах безмитної норми: податків немає.")
            return result

        share = taxed_qty / data.quantity
        value = money(price * share)
        weight_kg = None
        if kind.unit == "g":
            weight_kg = taxed_qty / 1000
        elif data.weight_g:
            weight_kg = data.weight_g * share / 1000
        if allowance > 0:
            result.notes.insert(0, (
                f"Оподатковано {_num(taxed_qty)} {unit} понад норму {_num(allowance)} {unit} "
                f"(вартість цієї частини: {value} EUR)."
            ))

        duty, duty_formula, _ = self._component(kind.duty, kind, taxed_qty, value, weight_kg, abv)
        excise, excise_formula, year = self._component(kind.excise, kind, taxed_qty, value, weight_kg, abv)
        if year != self.year:
            result.notes.append(f"Ставку акцизу на {self.year} рік у файлі ставок ще не внесено — використано ставку {year} року.")
        vat = money((value + duty + excise) * self.rules.vat_rate)
        result.lines.append(TaxLine("duty", "Мито", duty, duty_formula))
        result.lines.append(TaxLine("excise", "Акциз", excise, excise_formula))
        result.lines.append(TaxLine(
            "vat", "ПДВ", vat, f"{_pct(self.rules.vat_rate)} × ({value} + {duty} + {excise}) = {vat} EUR",
        ))
        return result
