"""Customs calculators (Strategy pattern): one class per delivery type.

Each calculator is pure: input value object + rule set -> Breakdown (EUR).
Currency conversion and persistence are handled outside, in services.
"""
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from app.customs.models import Breakdown, CarInput, EngineType, Origin, ParcelInput, Sender, TaxLine, money
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
        threshold = money(r.duty_free_threshold_eur)
        result = Breakdown(rules_key=r.key, goods_value_eur=goods, shipping_eur=shipping, notes=list(r.notes))

        if goods > r.simplified_limit_eur:
            result.notes.insert(0, (
                f"Вартість понад €{money(r.simplified_limit_eur)}: потрібне повне митне оформлення "
                "як для підприємств за повними ставками Митного тарифу — розрахунок орієнтовний."
            ))

        if goods > threshold:
            # Customs Code art. 374 p.7: duty and VAT only on the part above the threshold
            excess = goods - threshold
            duty = money(excess * r.duty_rate)
            vat = money((excess + duty) * r.vat_rate)
            result.lines.append(TaxLine(
                "duty", "Мито", duty, f"{_pct(r.duty_rate)} × ({goods} − {threshold}) = {duty} EUR",
            ))
            result.lines.append(TaxLine(
                "vat", "ПДВ", vat, f"{_pct(r.vat_rate)} × ({money(excess)} + {duty}) = {vat} EUR",
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


class CarCalculator(CustomsCalculator):
    def __init__(self, rules: CarRules = CAR_CURRENT, current_year: int | None = None):
        self.rules = rules
        self.current_year = current_year or date.today().year

    def age_coefficient(self, manufacture_year: int) -> int:
        """Full calendar years from the year after manufacture to the current year (TC 215.3.5-1)."""
        full_years = self.current_year - manufacture_year - 1
        return max(self.rules.age_coef_min, min(self.rules.age_coef_max, full_years))

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
        coef = self.age_coefficient(data.manufacture_year)
        amount = money(rate * litres * coef)
        return amount, f"{rate} € × {litres.normalize():f} л × {coef} (коеф. віку) = {amount} EUR"

    def calculate(self, data: CarInput) -> Breakdown:
        r = self.rules
        price = money(data.car_price_eur)
        shipping = money(data.shipping_eur)
        customs_value = price + shipping
        result = Breakdown(rules_key=r.key, goods_value_eur=price, shipping_eur=shipping, notes=list(r.notes))

        if data.engine_type is EngineType.ELECTRIC:
            duty_rate, duty_label = r.electric_duty_rate, "електромобіль"
        elif data.origin is Origin.EU:
            duty_rate, duty_label = r.duty_rate_eu, "авто походженням з ЄС"
        else:
            duty_rate, duty_label = r.duty_rate_other, "авто не з ЄС"
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
