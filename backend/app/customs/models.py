"""Value objects for the customs engine. All amounts are in EUR."""
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


class EngineType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"


class Origin(str, Enum):
    EU = "eu"
    OTHER = "other"


@dataclass(frozen=True)
class ParcelInput:
    goods_value_eur: Decimal
    shipping_eur: Decimal
    category: str = "other"


@dataclass(frozen=True)
class CarInput:
    car_price_eur: Decimal
    shipping_eur: Decimal
    engine_type: EngineType
    manufacture_year: int
    origin: Origin
    engine_volume_cc: int | None = None
    battery_kwh: Decimal | None = None


@dataclass(frozen=True)
class TaxLine:
    code: str  # duty | excise | vat
    label: str
    amount_eur: Decimal
    formula: str


@dataclass
class Breakdown:
    rules_key: str
    goods_value_eur: Decimal
    shipping_eur: Decimal
    lines: list[TaxLine] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def taxes_total_eur(self) -> Decimal:
        return money(sum((line.amount_eur for line in self.lines), Decimal("0")))

    @property
    def landed_total_eur(self) -> Decimal:
        return money(self.goods_value_eur + self.shipping_eur + self.taxes_total_eur)

    def line(self, code: str) -> TaxLine | None:
        return next((line for line in self.lines if line.code == code), None)
