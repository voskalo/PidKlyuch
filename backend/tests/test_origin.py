"""Country of ORIGIN vs country of DISPATCH (MK 36, 46, 280; free-trade agreements; Cabinet resolutions 426 / 1147)."""
from datetime import date
from decimal import Decimal as D

import pytest

from app.customs.calculators import CarCalculator, ImportBanned
from app.customs.models import CarInput, EngineType, Origin, ShippedFrom
from tests.test_calculate_api import CAR, PARCEL

TODAY = date(2026, 11, 18)


def duty(origin, shipped=ShippedFrom.ORIGIN, engine=EngineType.PETROL, cc=2000, year=2014, is_new=None, today=TODAY):
    calc = CarCalculator(today=today)
    b = calc.calculate(CarInput(car_price_eur=D("10000"), shipping_eur=D("0"), engine_type=engine, manufacture_year=year,
                                origin=origin, engine_volume_cc=cc if engine is not EngineType.ELECTRIC else None,
                                battery_kwh=D("60") if engine is EngineType.ELECTRIC else None, is_new=is_new,
                                shipped_from=shipped))
    return b.line("duty").amount_eur, b.notes


NEW_BIG = dict(cc=3500, year=2026)  # new petrol > 3000 cm3: normal rate 5% (8703 24 10 00), full rate 10%


@pytest.mark.parametrize("origin,used,new_big", [
    (Origin.EU, "0.00", "0.00"),
    (Origin.EFTA, "0.00", "0.00"),
    (Origin.UK, "0.00", "0.00"),
    (Origin.CANADA, "0.00", "0.00"),
    (Origin.ISRAEL, "0.00", "0.00"),
    (Origin.UAE, "670.00", "330.00"),      # 2/3 of the normal rate from 01.07.2026: 6.7% / 3.3%
    (Origin.OTHER, "1000.00", "500.00"),    # WTO / MFN normal rate: 10% / 5%
    (Origin.UNPROVEN, "1000.00", "1000.00"),  # full rate (MK 46 p.2): 10% even for the 5% line
])
def test_duty_by_country_of_origin(origin, used, new_big):
    assert duty(origin)[0] == D(used)
    assert duty(origin, **NEW_BIG)[0] == D(new_big)


@pytest.mark.parametrize("origin", [Origin.EU, Origin.EFTA, Origin.UK, Origin.CANADA, Origin.ISRAEL, Origin.UAE])
def test_shipped_from_a_third_country_loses_the_preference(origin):
    amount, notes = duty(origin, ShippedFrom.OTHER)
    assert amount == D("1000.00")
    assert duty(origin, ShippedFrom.OTHER, **NEW_BIG)[0] == D("500.00")
    assert any("пільга за угодою не діє" in n for n in notes)


def test_dispatch_does_not_change_normal_or_full_rates():
    assert duty(Origin.OTHER, ShippedFrom.OTHER)[0] == duty(Origin.OTHER)[0] == D("1000.00")
    assert duty(Origin.UNPROVEN, ShippedFrom.OTHER, **NEW_BIG)[0] == D("1000.00")


@pytest.mark.parametrize("origin", list(Origin))
def test_electric_cars_pay_0_whatever_the_origin(origin):
    assert duty(origin, engine=EngineType.ELECTRIC)[0] == D("0.00")


def test_shipped_from_russia_is_banned():
    with pytest.raises(ImportBanned):
        duty(Origin.OTHER, ShippedFrom.RUSSIA)
    with pytest.raises(ImportBanned):
        duty(Origin.EU, ShippedFrom.RUSSIA, engine=EngineType.ELECTRIC)


def test_agreement_dates():
    # UK preference starts 01.04.2026, UAE 01.07.2026: before that the normal rate, with a note
    amount, notes = duty(Origin.UK, today=date(2026, 3, 31))
    assert amount == D("1000.00") and any("діє з 01.04.2026" in n for n in notes)
    assert duty(Origin.UK, today=date(2026, 4, 1))[0] == D("0.00")
    assert duty(Origin.UAE, today=date(2026, 6, 30))[0] == D("1000.00")
    # after the approved period: the last known rate, with a "check it" note
    amount, notes = duty(Origin.EU, today=date(2027, 2, 1))
    assert amount == D("0.00") and any("треба перевірити" in n for n in notes)


def test_unproven_origin_explains_the_refund():
    _, notes = duty(Origin.UNPROVEN)
    assert any("ст. 46 ч. 2 МКУ" in n and "1095 днів" in n for n in notes)


# ---------------- API ----------------

@pytest.mark.parametrize("origin,expected", [("eu", "0.00"), ("uk", "0.00"), ("uae", "750.40"), ("other", "1120.00"), ("unproven", "1120.00")])
def test_api_origin(client, origin, expected):
    r = client.post("/api/calculate", json={**CAR, "origin": origin, "shipping_price": 1200})
    assert r.status_code == 200, r.text
    assert r.json()["lines"][0]["amount_eur"] == expected


def test_api_shipped_from_other_and_russia(client):
    r = client.post("/api/calculate", json={**CAR, "origin": "eu", "shipped_from": "other"})
    assert r.json()["lines"][0]["amount_eur"] == "1000.00"
    r = client.post("/api/calculate", json={**CAR, "shipped_from": "russia"})
    assert r.status_code == 422 and "banned" in r.json()["detail"][0]["msg"]
    assert client.post("/api/calculate", json={**CAR, "shipped_from": "mars"}).status_code == 422


def test_api_default_is_dispatch_from_origin(client):
    assert client.post("/api/calculate", json={**CAR, "origin": "eu"}).json()["lines"][0]["amount_eur"] == "0.00"


def test_car_origins_endpoint(client):
    rows = {o["key"]: o for o in client.get("/api/car/origins").json()}
    assert list(rows) == ["eu", "efta", "uk", "canada", "israel", "uae", "other", "unproven"]
    assert rows["eu"]["badge"] == "0%" and rows["other"]["badge"] == "10%" and rows["unproven"]["badge"] == "10%"


def test_parcel_and_excise_notes_explain_origin_vs_dispatch(client):
    parcel_notes = client.post("/api/calculate", json=PARCEL).json()["notes"]
    assert any("№ 426" in n and "№ 1147" in n and "не впливають" in n for n in parcel_notes)
    excise = {"delivery_type": "excise", "kind": "spirits", "quantity": 2, "item_price": 60}
    assert any("ПОХОДЖЕННЯ" in n and "№ 1147" in n for n in client.post("/api/calculate", json=excise).json()["notes"])
