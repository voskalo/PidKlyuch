"""Keeps the team spec (docs/customs-rules.md, section 5.3 JSON fixture) and the engine in agreement.

If this fails, either the law changed (update tax_rates.json AND the spec) or someone edited one without the other.
"""
import json
import re
from decimal import Decimal as D
from pathlib import Path

import pytest

from app.customs.calculators import CarCalculator, ParcelCalculator
from app.customs.models import CarInput, EngineType, Origin, ParcelInput, Sender, money
from app.customs.rules import PARCEL_CURRENT, PARCEL_JULY_2027

SPEC = Path(__file__).resolve().parents[2] / "docs" / "customs-rules.md"


def _fixture():
    match = re.search(r"### 5\.3.*?```json\n(.*?)```", SPEC.read_text(encoding="utf-8"), re.S)
    assert match, "docs/customs-rules.md must contain the section 5.3 JSON fixture"
    return json.loads(match.group(1))


FX = _fixture()
RATES = {k: D(v) for k, v in FX["nbu_test_rates_uah"].items()}


def eur(amount, currency):
    return money(D(amount) * RATES[currency] / RATES["EUR"])


def uah(amount_eur):
    return money(amount_eur * RATES["EUR"])


@pytest.mark.parametrize("case", FX["parcel_cases"], ids=lambda c: c["id"])
@pytest.mark.parametrize("rules_name,rules", [("current_rules", PARCEL_CURRENT), ("july_2027_rules", PARCEL_JULY_2027)])
def test_parcel_spec_case(case, rules_name, rules):
    i, exp = case["input"], case["expected"][rules_name]
    b = ParcelCalculator(rules).calculate(ParcelInput(
        eur(i["item_price"], i["currency"]), eur(i["shipping_cost"], i["currency"]), sender=Sender(i["sender"])))
    line = lambda code: b.line(code).amount_eur if b.line(code) else D("0.00")
    assert line("duty") == D(exp["duty_eur"])
    assert line("vat") == D(exp["vat_eur"])
    assert b.taxes_total_eur == D(exp["total_tax_eur"])
    assert uah(b.taxes_total_eur) == D(exp["total_tax_uah"])
    assert b.landed_total_eur == D(exp["total_landed_eur"])
    assert uah(b.landed_total_eur) == D(exp["total_landed_uah"])


@pytest.mark.parametrize("case", FX["car_cases"], ids=lambda c: c["id"])
def test_car_spec_case(case):
    i, exp = case["input"], case["expected"]
    calc = CarCalculator(current_year=FX["current_year"])
    b = calc.calculate(CarInput(
        eur(i["car_price"], i["currency"]), eur(i["shipping_price"], i["currency"]), EngineType(i["engine_type"]),
        i["production_year"], Origin(i["origin"]), i.get("engine_volume_cm3"),
        D(i["battery_capacity_kwh"]) if "battery_capacity_kwh" in i else None))
    assert calc.age_coefficient(i["production_year"]) == exp["k_age"]
    for code in ("duty", "excise", "vat"):
        assert b.line(code).amount_eur == D(exp[f"{code}_eur"]), code
    assert b.taxes_total_eur == D(exp["total_tax_eur"])
    assert uah(b.taxes_total_eur) == D(exp["total_tax_uah"])
    assert b.landed_total_eur == D(exp["total_landed_eur"])
    assert uah(b.landed_total_eur) == D(exp["total_landed_uah"])
