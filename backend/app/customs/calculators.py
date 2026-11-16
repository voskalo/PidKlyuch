"""Customs calculators (Strategy pattern): one class per delivery type.

Each calculator is pure: input value object + rule set -> Breakdown (EUR).
Currency conversion and persistence are handled outside, in services.
"""
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from app.customs.models import Breakdown, CarInput, EngineType, Origin, ParcelInput, TaxLine, money
from app.customs.rules import CAR_CURRENT, PARCEL_CURRENT, CarRules, ParcelRules

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
        result = Breakdown(rules_key=r.key, goods_value_eur=goods, shipping_eur=shipping, notes=list(r.notes))

        excess = max(ZERO, goods - r.duty_free_threshold_eur)
        duty = money(excess * r.duty_rate)
        if excess > 0:
            result.lines.append(TaxLine(
                "duty", "Мито", duty,
                f"{_pct(r.duty_rate)} × ({goods} − {money(r.duty_free_threshold_eur)}) = {duty} EUR",
            ))

        vat_base = goods if r.vat_on_full_value else excess
        if vat_base > 0:
            vat = money((vat_base + duty) * r.vat_rate)
            base_label = f"{money(vat_base)} + {duty}" if duty else f"{money(vat_base)}"
            result.lines.append(TaxLine(
                "vat", "ПДВ", vat, f"{_pct(r.vat_rate)} × ({base_label}) = {vat} EUR",
            ))

        if not result.lines:
            result.notes.insert(
                0, f"Вартість товару не перевищує €{money(r.duty_free_threshold_eur)}: податків немає."
            )
        return result


class CarCalculator(CustomsCalculator):
    def __init__(self, rules: CarRules = CAR_CURRENT, current_year: int | None = None):
        self.rules = rules
        self.current_year = current_year or date.today().year

    def age_coefficient(self, manufacture_year: int) -> int:
        age = self.current_year - manufacture_year
        return max(self.rules.age_coef_min, min(self.rules.age_coef_max, age))

    def _excise(self, data: CarInput) -> tuple[Decimal, str]:
        r = self.rules
        if data.engine_type is EngineType.ELECTRIC:
            if data.battery_kwh is None:
                raise ValueError("battery_kwh is required for electric cars")
            amount = money(r.electric_eur_per_kwh * Decimal(data.battery_kwh))
            return amount, f"{r.electric_eur_per_kwh} € × {data.battery_kwh} кВт·год = {amount} EUR"
        if data.engine_type is EngineType.HYBRID:
            return money(r.hybrid_flat_eur), f"фіксовано {money(r.hybrid_flat_eur)} EUR для гібрида"

        if not data.engine_volume_cc:
            raise ValueError("engine_volume_cc is required for petrol/diesel cars")
        cc = data.engine_volume_cc
        if data.engine_type is EngineType.PETROL:
            rate = r.petrol_rate_small if cc <= r.petrol_volume_limit_cc else r.petrol_rate_large
        else:
            rate = r.diesel_rate_small if cc <= r.diesel_volume_limit_cc else r.diesel_rate_large
        litres = Decimal(cc) / Decimal(1000)
        coef = self.age_coefficient(data.manufacture_year)
        amount = money(rate * litres * coef)
        return amount, f"{rate} € × {litres.normalize():f} л × {coef} (коеф. віку) = {amount} EUR"

    def calculate(self, data: CarInput) -> Breakdown:
        r = self.rules
        price = money(data.car_price_eur)
        shipping = money(data.shipping_eur)
        customs_value = price + shipping
        result = Breakdown(rules_key=r.key, goods_value_eur=price, shipping_eur=shipping, notes=list(r.notes))

        duty_rate = r.duty_rate_eu if data.origin is Origin.EU else r.duty_rate_other
        duty = money(customs_value * duty_rate)
        origin_label = "авто з ЄС" if data.origin is Origin.EU else "авто не з ЄС"
        result.lines.append(TaxLine(
            "duty", "Мито", duty, f"{_pct(duty_rate)} × {customs_value} ({origin_label}) = {duty} EUR",
        ))

        excise, excise_formula = self._excise(data)
        result.lines.append(TaxLine("excise", "Акциз", excise, excise_formula))

        vat = money((customs_value + duty + excise) * r.vat_rate)
        result.lines.append(TaxLine(
            "vat", "ПДВ", vat, f"{_pct(r.vat_rate)} × ({customs_value} + {duty} + {excise}) = {vat} EUR",
        ))
        return result
