"""Excise goods in luggage (MK 234 p.6, 235, 374 p.10, 376; TC 215.3, transitional subsection 5 items 17 and 48).

Expected values are worked out by hand from the statutes at 1 EUR = 50 UAH (see AGENTS.md §13).
"""
from decimal import Decimal as D

import pytest

from app.customs.calculators import ExciseCalculator
from app.customs.models import ExciseInput
from app.customs.rules import EXCISE_CURRENT
from tests.test_calculate_api import PARCEL

CALC = ExciseCalculator(eur_uah=D(50), current_year=2026)


def run(kind, qty, price, abv=None, weight=None, under_24h=False, calc=CALC):
    return calc.calculate(ExciseInput(kind, D(qty), D(price), D(abv) if abv else None,
                                      D(weight) if weight else None, under_24h))


def amounts(b):
    return {line.code: str(line.amount_eur) for line in b.lines}


@pytest.mark.parametrize("kind,qty,price,abv,weight,duty,excise,vat,total", [
    # 2 l whisky 40%, €60: 1 l over the 1 l norm, value €30; duty 0; excise 133.31 грн × 0.4 / 50 = 1.07
    ("spirits", "2", "60", "40", None, "0.00", "1.07", "6.21", "7.28"),
    # 400 cigarettes, €12: 200 over the norm, €6; excise max(61×0.2 + 12%×6 = 12.92; 82×0.2 = 16.40)
    ("cigarettes", "400", "12", None, None, "0.30", "16.40", "4.54", "21.24"),
    # expensive cigarettes: the ad valorem part beats the minimum: 61×0.2 + 12%×50 = 18.20
    ("cigarettes", "400", "100", None, None, "0.30", "18.20", "13.70", "32.20"),
    ("wine", "3", "30", None, None, "0.30", "0.00", "2.06", "2.36"),            # 0.01 грн/л excise rounds to 0
    ("beer", "10", "20", "5", None, "0.25", "0.30", "2.11", "2.66"),            # 59.82 × 5 л × 5% / 50
    ("e_liquid", "30", "15", None, None, "0.45", "9.00", "4.89", "14.34"),      # no norm; 300 €/л × 0.03 л
    ("petrol", "50", "85", None, None, "5.10", "9.02", "13.02", "27.14"),       # 20 l canister free; 300.8 €/1000 л
    ("diesel", "30", "45", None, None, "0.00", "2.54", "3.51", "6.05"),         # 253.8 €/1000 л
    ("cigars", "60", "120", None, "600", "2.00", "7.70", "5.94", "15.64"),      # 10 over 50; 100 g × 77 €/кг
    ("smoking_tobacco", "500", "40", None, None, "4.00", "19.25", "8.65", "31.90"),
    ("heated_tobacco", "400", "40", None, "300", "0.54", "28.32", "13.77", "42.63"),  # no norm; 70.8 €/1000
])
def test_hand_checked_cases(kind, qty, price, abv, weight, duty, excise, vat, total):
    b = run(kind, qty, price, abv, weight)
    assert amounts(b) == {"duty": duty, "excise": excise, "vat": vat}
    assert str(b.taxes_total_eur) == total
    assert b.landed_total_eur == D(price) + D(total)
    assert b.shipping_eur == D("0")


@pytest.mark.parametrize("kind,qty", [
    ("spirits", "1"), ("wine", "2"), ("sparkling_wine", "2"), ("beer", "5"), ("cigarettes", "200"),
    ("cigars", "50"), ("smoking_tobacco", "250"), ("petrol", "20"), ("diesel", "20"),
])
def test_within_allowance_is_tax_free(kind, qty):
    b = run(kind, qty, "50", abv=EXCISE_CURRENT.kinds[kind].abv_default and "40", weight="100")
    assert b.lines == [] and "у межах безмитної норми" in b.notes[0]


def test_under_24h_removes_the_alcohol_and_tobacco_allowance_but_not_fuel():
    assert amounts(run("spirits", "1", "30", "40", under_24h=True)) == {"duty": "0.00", "excise": "1.07", "vat": "6.21"}
    assert run("cigarettes", "200", "10", under_24h=True).lines  # all 200 taxed
    assert "менше 24 годин" in run("spirits", "1", "30", "40", under_24h=True).notes[0]
    assert run("petrol", "20", "40", under_24h=True).lines == []  # canister rule has no 24 h condition


def test_no_allowance_kinds_are_taxed_from_the_first_unit():
    assert run("e_liquid", "10", "5").lines and run("heated_tobacco", "20", "6", weight="15").lines


def test_only_the_part_above_the_norm_is_taxed_with_its_price_share():
    b = run("spirits", "3", "90", "40")  # 2 of 3 l taxed → value 60
    assert "(60.00 + 0.00 + 2.13)" in b.line("vat").formula
    assert "Оподатковано 2 л понад норму 1 л" in b.notes[0]


def test_rates_follow_the_calendar_year():
    b27 = run("cigarettes", "400", "12", calc=ExciseCalculator(eur_uah=D(50), current_year=2027))
    assert b27.line("excise").amount_eur == D("17.20")  # minimum 86 €/1000 in 2027
    b30 = run("petrol", "1020", "1000", calc=ExciseCalculator(eur_uah=D(50), current_year=2030))
    assert b30.line("excise").amount_eur == D("329.90")  # schedule ends in 2027 → 2027 rate, with a note
    assert any("2030" in n and "2027" in n for n in b30.notes)


def test_uah_rates_use_the_nbu_rate():
    a = run("spirits", "2", "60", "40", calc=ExciseCalculator(eur_uah=D("40"), current_year=2026))
    assert a.line("excise").amount_eur == D("1.33")  # 133.31 × 0.4 / 40
    assert "÷ 40 грн/€" in a.line("excise").formula


def test_calculator_rejects_bad_input():
    with pytest.raises(ValueError):
        run("absinthe", "1", "10")
    with pytest.raises(ValueError):
        run("cigars", "60", "120")  # weight missing
    with pytest.raises(ValueError):
        ExciseCalculator(eur_uah=D(0))


# ---------------- API ----------------

EXCISE = {"delivery_type": "excise", "kind": "spirits", "quantity": 2, "abv": 40, "item_price": 60, "currency": "EUR"}


def test_api_calculates_and_saves_excise(client):
    r = client.post("/api/calculate", json=EXCISE)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["delivery_type"] == "excise" and body["rules"] == "current"
    assert [l["code"] for l in body["lines"]] == ["duty", "excise", "vat"]
    assert body["taxes_total_eur"] == "7.28"  # conftest NBU: 1 EUR = 50 UAH
    assert any("ст. 235 МКУ" in n for n in body["notes"])


def test_api_converts_the_price_currency(client):
    r = client.post("/api/calculate", json={**EXCISE, "item_price": 2400, "currency": "UAH"})  # 2400 грн = €48
    assert r.json()["goods_value_eur"] == "48.00"


@pytest.mark.parametrize("patch,field", [
    ({"kind": "absinthe"}, "kind"),
    ({"quantity": 0}, "quantity"),
    ({"quantity": -1}, "quantity"),
    ({"quantity": "1.2345"}, "quantity"),
    ({"abv": 15}, None),                                    # spirits must be over 22%
    ({"abv": 97}, "abv"),
    ({"kind": "cigarettes", "quantity": "200.5", "abv": None}, None),  # pieces are whole
    ({"kind": "cigars", "quantity": 60, "abv": None}, None),           # weight_g required
    ({"item_price": -5}, "item_price"),
    ({"currency": "BTC"}, "currency"),
])
def test_api_rejects_user_mistakes(client, patch, field):
    r = client.post("/api/calculate", json={**EXCISE, **patch})
    assert r.status_code == 422, r.text
    if field:
        assert any(e["loc"][-1] == field for e in r.json()["detail"])


def test_api_abv_defaults_when_omitted(client):
    body = {k: v for k, v in EXCISE.items() if k != "abv"}
    assert client.post("/api/calculate", json=body).json()["taxes_total_eur"] == "7.28"  # default 40%


def test_compare_rules_still_parcel_only(client):
    assert client.post("/api/calculate/compare-rules", json=EXCISE).status_code == 422
    assert client.post("/api/calculate/compare-rules", json=PARCEL).status_code == 200


def test_kinds_endpoint_serves_the_form(client):
    r = client.get("/api/excise/kinds")
    assert r.status_code == 200
    body = r.json()
    kinds = {k["key"]: k for k in body["kinds"]}
    assert set(kinds) == set(EXCISE_CURRENT.kinds)
    assert kinds["spirits"]["unit"] == "l" and kinds["spirits"]["allowance"] == "1" and kinds["spirits"]["abv_required"]
    assert kinds["cigars"]["weight_required"] and kinds["e_liquid"]["unit"] == "ml" and kinds["e_liquid"]["allowance"] == "0"
    assert body["allowance_groups_24h"] == ["alcohol", "tobacco"]


def test_parcel_notes_state_the_postal_ban(client):
    notes = client.post("/api/calculate", json=PARCEL).json()["notes"]
    assert any("заборонені" in n and "ст. 235 МКУ" in n for n in notes)
