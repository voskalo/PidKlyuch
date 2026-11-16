"""Customs rule sets (rates, thresholds). Pure data, no logic.

⚠️ Values must be verified against official sources by Anton (docs/customs-rules.md).
Change numbers HERE only; calculators read everything from these objects.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ParcelRules:
    key: str
    title: str
    duty_free_threshold_eur: Decimal  # duty is charged only on the part above this
    duty_rate: Decimal
    vat_rate: Decimal
    vat_on_full_value: bool  # True: VAT on the whole goods value (July 2027); False: only above threshold
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CarRules:
    key: str
    title: str
    duty_rate_eu: Decimal
    duty_rate_other: Decimal
    vat_rate: Decimal
    # Excise: base rate (EUR per 1000 cm3) × engine litres × age coefficient
    petrol_rate_small: Decimal  # engine <= petrol_volume_limit_cc
    petrol_rate_large: Decimal
    petrol_volume_limit_cc: int
    diesel_rate_small: Decimal  # engine <= diesel_volume_limit_cc
    diesel_rate_large: Decimal
    diesel_volume_limit_cc: int
    hybrid_flat_eur: Decimal
    electric_eur_per_kwh: Decimal
    age_coef_min: int
    age_coef_max: int
    notes: tuple[str, ...] = ()


PARCEL_CURRENT = ParcelRules(
    key="current",
    title="Чинні правила",
    duty_free_threshold_eur=Decimal("150"),
    duty_rate=Decimal("0.10"),
    vat_rate=Decimal("0.20"),
    vat_on_full_value=False,
    notes=(
        "Безмитний ліміт €150 діє на одну посилку; вартість доставки до ліміту не включено.",
        "Мито 10% і ПДВ 20% нараховуються лише на суму перевищення ліміту.",
    ),
)

PARCEL_JULY_2027 = ParcelRules(
    key="july_2027",
    title="Правила з липня 2027",
    duty_free_threshold_eur=Decimal("150"),
    duty_rate=Decimal("0.10"),
    vat_rate=Decimal("0.20"),
    vat_on_full_value=True,
    notes=(
        "З липня 2027 ПДВ 20% сплачується з кожної посилки, незалежно від вартості.",
        "Мито 10% і далі нараховується лише на суму понад €150 (припущення, потребує перевірки).",
    ),
)

CAR_CURRENT = CarRules(
    key="current",
    title="Чинні правила",
    duty_rate_eu=Decimal("0"),
    duty_rate_other=Decimal("0.10"),
    vat_rate=Decimal("0.20"),
    petrol_rate_small=Decimal("50"),
    petrol_rate_large=Decimal("100"),
    petrol_volume_limit_cc=3000,
    diesel_rate_small=Decimal("75"),
    diesel_rate_large=Decimal("150"),
    diesel_volume_limit_cc=3500,
    hybrid_flat_eur=Decimal("100"),
    electric_eur_per_kwh=Decimal("1"),
    age_coef_min=1,
    age_coef_max=15,
    notes=(
        "Митна вартість = ціна авто + доставка до кордону України.",
        "ПДВ 20% нараховується на (митна вартість + мито + акциз).",
        "Без урахування зборів за реєстрацію, сертифікацію та послуг брокера.",
    ),
)

PARCEL_RULES: dict[str, ParcelRules] = {r.key: r for r in (PARCEL_CURRENT, PARCEL_JULY_2027)}
