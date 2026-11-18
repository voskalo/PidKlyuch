from datetime import date as Date
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import Body
from pydantic import BaseModel, Field, model_validator

from app.customs.rules import EXCISE_CURRENT

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


ExciseKindKey = Literal["beer", "wine", "sparkling_wine", "spirits", "cigarettes", "cigars", "smoking_tobacco",
                        "heated_tobacco", "e_liquid", "petrol", "diesel"]
assert set(ExciseKindKey.__args__) == set(EXCISE_CURRENT.kinds), "keep ExciseKindKey in sync with tax_rates.json"


class ExciseIn(BaseModel):
    """Excise goods in one adult's luggage (alcohol, tobacco, e-liquids, fuel in a canister).

    Not for parcels: MK 235 bans alcohol/tobacco/e-liquids in postal and express items to private persons.
    """
    delivery_type: Literal["excise"]
    kind: ExciseKindKey
    quantity: Decimal = Field(gt=0, le=100_000, max_digits=9, decimal_places=3)  # l | ml | pcs | g, see the kind
    item_price: Amount  # price paid for the whole quantity
    currency: Currency = "EUR"
    abv: Decimal | None = Field(default=None, gt=0, le=96, max_digits=4, decimal_places=1)  # % vol (beer, spirits)
    weight_g: Decimal | None = Field(default=None, gt=0, le=100_000, max_digits=9, decimal_places=1)  # cigars, sticks
    under_24h: bool = False  # abroad < 24 h: no allowance for alcohol and tobacco (MK 376 p.3)

    @model_validator(mode="after")
    def _kind_fields(self):
        kind = EXCISE_CURRENT.kinds[self.kind]
        if kind.unit == "pcs" and self.quantity != self.quantity.to_integral_value():
            raise ValueError(f"quantity of {self.kind} is a whole number of pieces")
        if kind.abv_required and self.abv is not None and not (kind.abv_min <= self.abv <= kind.abv_max):
            raise ValueError(f"abv for {self.kind} must be between {kind.abv_min} and {kind.abv_max}")
        if kind.weight_required and self.weight_g is None:
            raise ValueError(f"weight_g is required for {self.kind}")
        return self


# Body(discriminator=...) makes FastAPI validate ONLY the model selected by delivery_type, so a bad car
# gets car errors (not "Input should be 'parcel'" from trying ParcelIn first).
CalculationIn = Annotated[ParcelIn | CarIn | ExciseIn, Body(discriminator="delivery_type")]


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


class ExciseKindOut(BaseModel):
    key: str
    label: str
    group: str
    unit: str
    allowance: Decimal
    allowance_note: str
    abv_required: bool
    abv_default: Decimal | None
    abv_min: Decimal | None
    abv_max: Decimal | None
    weight_required: bool


class ExciseKindsOut(BaseModel):
    kinds: list[ExciseKindOut]
    allowance_groups_24h: list[str]  # groups that lose the allowance after < 24 h abroad
    notes: list[str]


class RatesOut(BaseModel):
    date: Date
    source: str
    uah_per_unit: dict[str, Decimal]
