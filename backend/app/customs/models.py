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
    """Country of ORIGIN (where the car was made, MK 36) — decides the duty column."""
    EU = "eu"
    EFTA = "efta"
    UK = "uk"
    CANADA = "canada"
    ISRAEL = "israel"
    UAE = "uae"
    OTHER = "other"  # WTO / most-favoured-nation country (USA, Japan, Korea, China, Turkey, ...): normal rate
    UNPROVEN = "unproven"  # origin not established: full rate (MK 46 p.2)


class ShippedFrom(str, Enum):
    """Country of DISPATCH (where the car is shipped to Ukraine from) — a separate term from origin."""
    ORIGIN = "origin"  # from the origin country / agreement area: preferences can apply
    OTHER = "other"  # from a third country: free-trade preference lost (direct transport rule)
    RUSSIA = "russia"  # from or through russia: import banned (Cabinet resolution 426)


class Sender(str, Enum):
    MARKETPLACE = "marketplace"  # online shop / marketplace purchase (distance sale)
    PRIVATE = "private"  # non-commercial parcel from a private person


@dataclass(frozen=True)
class ParcelInput:
    goods_value_eur: Decimal
    shipping_eur: Decimal
    sender: Sender = Sender.MARKETPLACE


@dataclass(frozen=True)
class CarInput:
    car_price_eur: Decimal
    shipping_eur: Decimal
    engine_type: EngineType
    manufacture_year: int
    origin: Origin
    engine_volume_cc: int | None = None
    battery_kwh: Decimal | None = None
    is_new: bool | None = None  # never used before (Customs Tariff "нові"); None = derive from manufacture_year
    shipped_from: ShippedFrom = ShippedFrom.ORIGIN


@dataclass(frozen=True)
class ExciseInput:
    """Excise goods brought in luggage by one adult (alcohol, tobacco, e-liquids, fuel in a canister)."""
    kind: str  # key of excise_rule_sets.*.kinds in tax_rates.json
    quantity: Decimal  # in the kind's unit: l | ml | pcs | g
    price_eur: Decimal  # price paid for the whole quantity
    abv: Decimal | None = None  # % alcohol by volume (beer, spirits)
    weight_g: Decimal | None = None  # net weight of the whole quantity (cigars, heated tobacco sticks)
    under_24h: bool = False  # abroad less than 24 hours: no duty-free allowance (MK 376 p.3)


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
