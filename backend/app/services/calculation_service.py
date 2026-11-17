"""Use case: API input -> EUR conversion -> customs engine -> response with UAH amounts."""
from decimal import Decimal

from app.api.schemas_calc import CalculationOut, CarIn, ParcelIn, TaxLineOut
from app.customs.calculators import CarCalculator, ParcelCalculator
from app.customs.models import Breakdown, CarInput, EngineType, Origin, ParcelInput, Sender, money
from app.customs.rules import CAR_CURRENT, PARCEL_RULES, TAX_RATES
from app.services.rates_service import RateTable


class CalculationService:
    def __init__(self, rates: RateTable):
        self.rates = rates

    def _eur(self, amount: Decimal, currency: str) -> Decimal:
        return money(self.rates.to_eur(amount, currency))

    def _uah(self, amount_eur: Decimal) -> Decimal:
        return money(self.rates.eur_to_uah(amount_eur))

    def _breakdown(self, body: ParcelIn | CarIn) -> Breakdown:
        if isinstance(body, ParcelIn):
            data = ParcelInput(
                goods_value_eur=self._eur(body.item_price, body.currency),
                shipping_eur=self._eur(body.shipping_price, body.currency),
                category=body.category,
                sender=Sender(body.sender),
            )
            return ParcelCalculator(PARCEL_RULES[body.rules]).calculate(data)
        data = CarInput(
            car_price_eur=self._eur(body.car_price, body.currency),
            shipping_eur=self._eur(body.shipping_price, body.currency),
            engine_type=EngineType(body.engine_type),
            manufacture_year=body.manufacture_year,
            origin=Origin(body.origin),
            engine_volume_cc=body.engine_volume_cc,
            battery_kwh=body.battery_kwh,
        )
        return CarCalculator(CAR_CURRENT).calculate(data)

    def calculate(self, body: ParcelIn | CarIn) -> CalculationOut:
        b = self._breakdown(body)
        notes = list(b.notes)
        if body.currency != "EUR":
            notes.append(
                f"Конвертація за курсом НБУ на {self.rates.date:%d.%m.%Y}: "
                f"1 {body.currency} = {self.rates.uah_per_unit[body.currency]} грн, "
                f"1 EUR = {self.rates.uah_per_unit['EUR']} грн."
            )
        if self.rates.source == "fallback":
            notes.append("Курс НБУ тимчасово недоступний — використано орієнтовний курс.")
        return CalculationOut(
            delivery_type=body.delivery_type,
            rules=b.rules_key,
            input_currency=body.currency,
            rate_date=self.rates.date,
            rate_source=self.rates.source,
            eur_uah=self.rates.uah_per_unit["EUR"].quantize(Decimal("0.0001")),
            goods_value_eur=b.goods_value_eur,
            shipping_eur=b.shipping_eur,
            lines=[
                TaxLineOut(code=l.code, label=l.label, amount_eur=l.amount_eur,
                           amount_uah=self._uah(l.amount_eur), formula=l.formula)
                for l in b.lines
            ],
            taxes_total_eur=b.taxes_total_eur,
            taxes_total_uah=self._uah(b.taxes_total_eur),
            landed_total_eur=b.landed_total_eur,
            landed_total_uah=self._uah(b.landed_total_eur),
            notes=notes,
            rates_version=TAX_RATES.version,
            rates_verified_at=TAX_RATES.verified_at,
        )
