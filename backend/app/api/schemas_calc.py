from datetime import date as Date
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import Body
from pydantic import BaseModel, Field, model_validator

Currency = Literal["EUR", "USD", "UAH", "GBP", "PLN"]
Amount = Annotated[Decimal, Field(ge=0, le=10_000_000, max_digits=12, decimal_places=2)]


class ParcelIn(BaseModel):
    # No goods category: Customs Code 374 p.7 taxes all non-excise goods in a parcel the same way.
    # A "category" sent by old clients is ignored (pydantic drops unknown fields).
    delivery_type: Literal["parcel"]
    item_price: Amount
    shipping_price: Amount = Decimal("0")
    currency: Currency = "EUR"
    rules: Literal["current", "july_2027"] = "current"
    sender: Literal["marketplace", "private"] = "marketplace"


class CarIn(BaseModel):
    delivery_type: Literal["car"]
    car_price: Amount
    shipping_price: Amount = Decimal("0")
    currency: Currency = "EUR"
    engine_type: Literal["petrol", "diesel", "hybrid", "electric"]
    engine_volume_cc: int | None = Field(default=None, gt=0, le=10_000)
    battery_kwh: Decimal | None = Field(default=None, gt=0, le=500)
    manufacture_year: int = Field(ge=1950, le=Date.today().year + 1)
    origin: Literal["eu", "other"] = "other"
    # Customs Tariff "new" (never used). Optional: if omitted, a car made this year or later counts as new.
    is_new: bool | None = None

    @model_validator(mode="after")
    def _engine_fields(self):
        if self.engine_type == "electric" and self.battery_kwh is None:
            raise ValueError("battery_kwh is required for electric cars")
        if self.engine_type in ("petrol", "diesel", "hybrid") and self.engine_volume_cc is None:
            raise ValueError("engine_volume_cc is required for petrol, diesel and hybrid cars")
        return self


# Body(discriminator=...) makes FastAPI validate ONLY the model selected by delivery_type, so a bad car
# gets car errors (not "Input should be 'parcel'" from trying ParcelIn first).
CalculationIn = Annotated[ParcelIn | CarIn, Body(discriminator="delivery_type")]


class TaxLineOut(BaseModel):
    code: str
    label: str
    amount_eur: Decimal
    amount_uah: Decimal
    formula: str


class CalculationOut(BaseModel):
    delivery_type: str
    rules: str
    input_currency: str
    rate_date: Date
    rate_source: str
    eur_uah: Decimal
    goods_value_eur: Decimal
    shipping_eur: Decimal
    lines: list[TaxLineOut]
    taxes_total_eur: Decimal
    taxes_total_uah: Decimal
    landed_total_eur: Decimal
    landed_total_uah: Decimal
    notes: list[str]
    rates_version: str
    rates_verified_at: Date
    calculation_id: int | None = None


class CompareRulesOut(BaseModel):
    current: CalculationOut
    july_2027: CalculationOut


class RatesOut(BaseModel):
    date: Date
    source: str
    uah_per_unit: dict[str, Decimal]
