"""Customs engine tests, based on the rules verified on 16.11.2026 (sources in app/customs/tax_rates.json).

Expected values are calculated by hand from the legal formulas, not taken from the code.
"""
from decimal import Decimal as D

import pytest

from app.customs.calculators import CarCalculator, ParcelCalculator
from app.customs.models import CarInput, EngineType, Origin, ParcelInput, Sender
from app.customs.rules import PARCEL_JULY_2027


def parcel(goods, shipping="0", sender=Sender.MARKETPLACE):
    return ParcelInput(goods_value_eur=D(goods), shipping_eur=D(shipping), sender=sender)


# --- Parcels: current rules (Customs Code art. 374 p.7) ----------------------

def test_pitch_example_200_eur_parcel_adds_16():
    b = ParcelCalculator().calculate(parcel("200", "15"))
    assert b.line("duty").amount_eur == D("5.00")   # 10% × (200 − 150)
    assert b.line("vat").amount_eur == D("11.00")   # 20% × (50 + 5)
    assert b.taxes_total_eur == D("16.00")
    assert b.landed_total_eur == D("231.00")
    assert "200.00 − 150.00" in b.line("duty").formula


@pytest.mark.parametrize("goods", ["0", "99.99", "150", "150.00"])
def test_parcel_at_or_below_threshold_is_tax_free(goods):
    b = ParcelCalculator().calculate(parcel(goods, "20"))
    assert b.lines == []
    assert b.taxes_total_eur == D("0.00")


def test_shipping_does_not_count_toward_threshold():
    b = ParcelCalculator().calculate(parcel("140", "30"))
    assert b.taxes_total_eur == D("0.00")


def test_parcel_just_above_threshold():
    b = ParcelCalculator().calculate(parcel("150.10"))
    assert b.line("duty").amount_eur == D("0.01")
    assert b.line("vat").amount_eur == D("0.02")  # 20% × 0.11 = 0.022 -> 0.02


def test_parcel_large_value():
    b = ParcelCalculator().calculate(parcel("1000"))
    assert b.taxes_total_eur == D("272.00")  # duty 85, VAT 20% × 935 = 187


def test_parcel_over_10000_warns_about_commercial_clearance():
    b = ParcelCalculator().calculate(parcel("12000"))
    assert "повне митне оформлення" in b.notes[0]


# --- Parcels: July 2027 rules (Laws 5025-IX / 5026-IX) -----------------------

def test_2027_marketplace_parcel_under_threshold_pays_vat_only():
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("40"))
    assert b.line("duty") is None
    assert b.line("vat").amount_eur == D("8.00")


def test_2027_vat_at_threshold():
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("150"))
    assert b.line("vat").amount_eur == D("30.00")
    assert b.line("duty") is None


def test_2027_private_gift_up_to_45_is_exempt():
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("45", sender=Sender.PRIVATE))
    assert b.lines == []
    assert "€45" in b.notes[0]


def test_2027_private_parcel_above_45_pays_vat():
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("100", sender=Sender.PRIVATE))
    assert b.line("vat").amount_eur == D("20.00")


def test_2027_above_threshold_taxes_the_full_value():
    # Law 5026-IX item 19: duty base = whole invoice value; Law 5025-IX item 6: VAT base = whole value + duty
    b = ParcelCalculator(PARCEL_JULY_2027).calculate(parcel("200", "20"))
    assert b.line("duty").amount_eur == D("20.00")   # 10% × 200
    assert b.line("vat").amount_eur == D("44.00")    # 20% × (200 + 20)
    assert b.taxes_total_eur == D("64.00")
    assert b.landed_total_eur == D("284.00")
    assert b.line("duty").formula == "10% × 200.00 = 20.00 EUR"
    assert b.rules_key == "july_2027"


@pytest.mark.parametrize("goods,current,july_2027", [
    ("150.00", "0.00", "30.00"),      # at the limit: today free, 2027 VAT only
    ("150.01", "0.00", "48.00"),      # today: 0.001 duty and 0.002 VAT round to 0; 2027: duty 15.00 + VAT 33.00
    ("276.00", "40.32", "88.32"),     # docs/customs-rules.md TC-P4 (€276): 2027 duty 27.60 + VAT 60.72
    ("1000.00", "272.00", "320.00"),  # TC-P5: 2027 duty 100 + VAT 220
])
def test_current_vs_2027_totals(goods, current, july_2027):
    assert ParcelCalculator().calculate(parcel(goods)).taxes_total_eur == D(current)
    assert ParcelCalculator(PARCEL_JULY_2027).calculate(parcel(goods)).taxes_total_eur == D(july_2027)


def test_sender_does_not_matter_under_current_rules():
    b = ParcelCalculator().calculate(parcel("40", sender=Sender.PRIVATE))
    assert b.lines == []


# --- Cars (Tax Code 215.3.5-1) -----------------------------------------------

def car(**kw):
    defaults = dict(car_price_eur=D("10000"), shipping_eur=D("0"), engine_type=EngineType.PETROL,
                    manufacture_year=2014, origin=Origin.OTHER, engine_volume_cc=2000)
    defaults.update(kw)
    return CarInput(**defaults)


@pytest.mark.parametrize("year,coef", [
    (2026, 1), (2025, 1), (2024, 1), (2023, 2), (2014, 11), (2011, 14), (2010, 15), (1990, 15),
])
def test_age_coefficient_counts_full_years_from_year_after_manufacture(year, coef):
    assert CarCalculator(current_year=2026).age_coefficient(year) == coef


def test_non_eu_petrol_2014_car():
    # duty 1000; excise 50 × 2.0 × 11 = 1100; VAT 20% × (10000 + 1000 + 1100) = 2420
    b = CarCalculator(current_year=2026).calculate(car())
    assert b.line("duty").amount_eur == D("1000.00")
    assert b.line("excise").amount_eur == D("1100.00")
    assert b.line("vat").amount_eur == D("2420.00")
    assert b.taxes_total_eur == D("4520.00")


def test_pitch_upper_bound_4640_is_a_2013_car():
    # coef 12: excise 1200, VAT 20% × 12200 = 2440 -> 1000 + 1200 + 2440
    b = CarCalculator(current_year=2026).calculate(car(manufacture_year=2013))
    assert b.taxes_total_eur == D("4640.00")


def test_pitch_lower_bound_2048_eu_new_small_engine():
    # EU origin: duty 0; excise 50 × 0.8 × 1 = 40; VAT 20% × 10040 = 2008
    b = CarCalculator(current_year=2026).calculate(
        car(origin=Origin.EU, engine_volume_cc=800, manufacture_year=2026)
    )
    assert b.taxes_total_eur == D("2048.00")


def test_shipping_is_part_of_customs_value():
    b = CarCalculator(current_year=2026).calculate(car(shipping_eur=D("1000")))
    assert b.line("duty").amount_eur == D("1100.00")


def test_engine_volume_thresholds_and_large_engine_rates():
    calc = CarCalculator(current_year=2026)
    exc = lambda **kw: calc.calculate(car(manufacture_year=2022, **kw)).line("excise").amount_eur  # coef 3
    assert exc(engine_volume_cc=3000) == D("450.00")    # 50 × 3.0 × 3 (3000 cc is still "small")
    assert exc(engine_volume_cc=3500) == D("1050.00")   # 100 × 3.5 × 3
    assert exc(engine_type=EngineType.DIESEL, engine_volume_cc=2000) == D("450.00")   # 75 × 2 × 3
    assert exc(engine_type=EngineType.DIESEL, engine_volume_cc=3500) == D("787.50")   # 75 × 3.5 × 3
    assert exc(engine_type=EngineType.DIESEL, engine_volume_cc=4000) == D("1800.00")  # 150 × 4 × 3


def test_hybrid_pays_excise_by_combustion_engine():
    b = CarCalculator(current_year=2026).calculate(car(engine_type=EngineType.HYBRID, manufacture_year=2022))
    assert b.line("excise").amount_eur == D("300.00")  # petrol rate: 50 × 2.0 × 3


@pytest.mark.parametrize("engine,cc,year,is_new,rate", [
    (EngineType.PETROL, 3500, 2026, None, "5"),    # new (this year) petrol > 3000 cm3 → 5% (tariff 8703 24 10 00)
    (EngineType.HYBRID, 3500, 2026, None, "5"),    # new petrol hybrid > 3000 cm3 → 5% (8703 40 10 80 / 60 10 80)
    (EngineType.PETROL, 3000, 2026, None, "10"),   # exactly 3000 cm3 is not "over 3000"
    (EngineType.PETROL, 3500, 2024, None, "10"),   # used petrol > 3000 → 10%
    (EngineType.PETROL, 3500, 2024, True, "5"),    # user says new (e.g. unsold 2024 stock) → 5%
    (EngineType.PETROL, 3500, 2026, False, "10"),  # user says used → 10%
    (EngineType.DIESEL, 3500, 2026, None, "10"),   # new diesel > 3000 → still 10% (8703 33 19 00)
])
def test_duty_rate_depends_on_new_and_engine(engine, cc, year, is_new, rate):
    b = CarCalculator(current_year=2026).calculate(
        car(engine_type=engine, engine_volume_cc=cc, manufacture_year=year, is_new=is_new)
    )
    assert b.line("duty").amount_eur == D("10000") * D(rate) / 100


@pytest.mark.parametrize("engine,year,is_new,k,new_label", [
    (EngineType.DIESEL, 2014, True, 1, True),     # never-used 2014 diesel: K_age = 1, not 11 (TC 215.3.5-1)
    (EngineType.PETROL, 2020, True, 1, True),     # never-used 2020 petrol, EU or not: K_age = 1
    (EngineType.HYBRID, 2014, True, 1, True),
    (EngineType.DIESEL, 2014, None, 11, False),   # not said → by year
    (EngineType.DIESEL, 2014, False, 11, False),  # said used → by year
    (EngineType.DIESEL, 2026, False, 1, False),   # used but this year's → 1 anyway (minimum)
    (EngineType.DIESEL, 2024, True, 1, False),    # new, and by year also 1 → no "нове авто" remark needed
])
def test_new_car_age_coefficient_is_1(engine, year, is_new, k, new_label):
    b = CarCalculator(current_year=2026).calculate(
        car(engine_type=engine, manufacture_year=year, is_new=is_new, origin=Origin.EU)
    )
    base = 75 if engine is EngineType.DIESEL else 50
    excise = b.line("excise")
    assert excise.amount_eur == D(base * 2 * k)
    assert f"× {k} (коеф. віку" in excise.formula
    assert ("нове авто" in excise.formula) is new_label


def test_new_car_k_age_flows_into_vat():
    b = CarCalculator(current_year=2026).calculate(
        car(engine_type=EngineType.DIESEL, manufacture_year=2014, is_new=True)
    )
    # duty 10% of 10000 = 1000, excise 75 × 2 × 1 = 150, VAT 20% × (10000 + 1000 + 150) = 2230
    assert [l.amount_eur for l in b.lines] == [D("1000.00"), D("150.00"), D("2230.00")]
    assert b.taxes_total_eur == D("3380.00")


def test_eu_origin_beats_reduced_rate():
    b = CarCalculator(current_year=2026).calculate(
        car(engine_volume_cc=3500, manufacture_year=2026, origin=Origin.EU)
    )
    assert b.line("duty").amount_eur == D("0.00")


def test_electric_car_no_duty_but_vat_since_2026():
    b = CarCalculator(current_year=2026).calculate(
        car(engine_type=EngineType.ELECTRIC, engine_volume_cc=None, battery_kwh=D("75"))
    )
    assert b.line("duty").amount_eur == D("0.00")      # 0% regardless of origin
    assert b.line("excise").amount_eur == D("75.00")   # 1 € × 75 kWh
    assert b.line("vat").amount_eur == D("2015.00")    # 20% × 10075
    assert b.taxes_total_eur == D("2090.00")


def test_missing_engine_data_raises():
    calc = CarCalculator(current_year=2026)
    with pytest.raises(ValueError):
        calc.calculate(car(engine_volume_cc=None))
    with pytest.raises(ValueError):
        calc.calculate(car(engine_type=EngineType.ELECTRIC, engine_volume_cc=None))
