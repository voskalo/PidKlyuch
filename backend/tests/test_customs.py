"""Customs engine tests. Pitch examples are used as sanity checks.

Anton: add verified cases from docs/customs-rules.md here.
"""
from decimal import Decimal as D

import pytest

from app.customs.calculators import CarCalculator, ParcelCalculator
from app.customs.models import CarInput, EngineType, Origin, ParcelInput
from app.customs.rules import PARCEL_JULY_2027


def parcel(goods, shipping="0"):
    return ParcelInput(goods_value_eur=D(goods), shipping_eur=D(shipping))


# --- Parcels: current rules --------------------------------------------------

def test_pitch_example_200_eur_parcel_adds_16():
    b = ParcelCalculator().calculate(parcel("200", "15"))
    assert b.line("duty").amount_eur == D("5.00")
    assert b.line("vat").amount_eur == D("11.00")
    assert b.taxes_total_eur == D("16.00")
    assert b.landed_total_eur == D("231.00")
    assert "200.00 − 150.00" in b.line("duty").formula


@pytest.mark.parametrize("goods", ["0", "99.99", "150", "150.00"])
def test_parcel_at_or_below_threshold_is_tax_free(goods):
    b = ParcelCalculator().calculate(parcel(goods, "20"))
    assert b.lines == []
    assert b.taxes_total_eur == D("0.00")


def test_parcel_just_above_threshold():
    b = ParcelCalculator().calculate(parcel("150.10"))
    assert b.line("duty").amount_eur == D("0.01")
    assert b.line("vat").amount_eur == D("0.02")  # 20% × 0.11 = 0.022 -> 0.02


def test_parcel_large_value():
    b = ParcelCalculator().calculate(parcel("1000"))
    # excess 850, duty 85, VAT 20% × 935 = 187
    assert b.taxes_total_eur == D("272.00")


# --- Parcels: July 2027 rules ------------------------------------------------

def test_2027_vat_on_cheap_parcel():
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("40"))
    assert b.line("duty") is None
    assert b.line("vat").amount_eur == D("8.00")


def test_2027_vat_on_full_value_above_threshold():
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("200"))
    # duty 10% × 50 = 5; VAT 20% × (200 + 5) = 41
    assert b.line("duty").amount_eur == D("5.00")
    assert b.line("vat").amount_eur == D("41.00")
    assert b.rules_key == "july_2027"


# --- Cars --------------------------------------------------------------------

def car(**kw):
    defaults = dict(car_price_eur=D("10000"), shipping_eur=D("0"), engine_type=EngineType.PETROL,
                    manufacture_year=2014, origin=Origin.OTHER, engine_volume_cc=2000)
    defaults.update(kw)
    return CarInput(**defaults)


def test_pitch_upper_bound_10k_car_4640():
    # non-EU petrol 2.0 l, 12 years old: duty 1000, excise 50×2×12=1200, VAT 20%×12200=2440
    b = CarCalculator(current_year=2026).calculate(car())
    assert b.line("duty").amount_eur == D("1000.00")
    assert b.line("excise").amount_eur == D("1200.00")
    assert b.line("vat").amount_eur == D("2440.00")
    assert b.taxes_total_eur == D("4640.00")


def test_pitch_lower_bound_10k_car_2048():
    # EU-origin, new petrol 0.8 l: duty 0, excise 50×0.8×1=40, VAT 20%×10040=2008
    b = CarCalculator(current_year=2026).calculate(
        car(origin=Origin.EU, engine_volume_cc=800, manufacture_year=2026)
    )
    assert b.taxes_total_eur == D("2048.00")


def test_shipping_is_part_of_customs_value():
    b = CarCalculator(current_year=2026).calculate(car(shipping_eur=D("1000")))
    assert b.line("duty").amount_eur == D("1100.00")


@pytest.mark.parametrize("year,coef", [(2026, 1), (2025, 1), (2024, 2), (2014, 12), (2000, 15), (1990, 15)])
def test_age_coefficient_bounds(year, coef):
    assert CarCalculator(current_year=2026).age_coefficient(year) == coef


def test_large_engine_rates():
    calc = CarCalculator(current_year=2026)
    petrol = calc.calculate(car(engine_volume_cc=3500, manufacture_year=2024))
    assert petrol.line("excise").amount_eur == D("700.00")  # 100 × 3.5 × 2
    diesel = calc.calculate(car(engine_type=EngineType.DIESEL, engine_volume_cc=2000, manufacture_year=2024))
    assert diesel.line("excise").amount_eur == D("300.00")  # 75 × 2 × 2
    big_diesel = calc.calculate(car(engine_type=EngineType.DIESEL, engine_volume_cc=4000, manufacture_year=2024))
    assert big_diesel.line("excise").amount_eur == D("1200.00")  # 150 × 4 × 2


def test_electric_and_hybrid_excise():
    calc = CarCalculator(current_year=2026)
    ev = calc.calculate(car(engine_type=EngineType.ELECTRIC, engine_volume_cc=None, battery_kwh=D("75")))
    assert ev.line("excise").amount_eur == D("75.00")
    hybrid = calc.calculate(car(engine_type=EngineType.HYBRID))
    assert hybrid.line("excise").amount_eur == D("100.00")


def test_missing_engine_data_raises():
    calc = CarCalculator(current_year=2026)
    with pytest.raises(ValueError):
        calc.calculate(car(engine_volume_cc=None))
    with pytest.raises(ValueError):
        calc.calculate(car(engine_type=EngineType.ELECTRIC, engine_volume_cc=None))
