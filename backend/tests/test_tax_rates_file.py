"""The rates data file: loads, validates, and every rule cites a source."""
import json
from decimal import Decimal as D

import pytest

from app.customs.rules import DEFAULT_RATES_PATH, TAX_RATES, load_tax_rates


def test_default_file_loads_with_expected_values():
    assert TAX_RATES.parcel["current"].duty_free_threshold_eur == D("150")
    assert TAX_RATES.parcel["july_2027"].private_exempt_up_to_eur == D("45")
    car = TAX_RATES.car["current"]
    assert car.excise_base["petrol"].rate_for(3000) == D("50")
    assert car.excise_base["diesel"].rate_for(3501) == D("150")
    assert car.vat_rate == D("0.2")


def test_every_rule_set_cites_existing_sources():
    for rule in (*TAX_RATES.parcel.values(), *TAX_RATES.car.values()):
        assert rule.sources, f"{rule.key} has no sources"
        assert all(s in TAX_RATES.sources for s in rule.sources)


def _write(tmp_path, mutate):
    raw = json.loads(DEFAULT_RATES_PATH.read_text(encoding="utf-8"))
    mutate(raw)
    p = tmp_path / "rates.json"
    p.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return p


def test_alternative_file_via_path(tmp_path):
    p = _write(tmp_path, lambda r: r["parcel_rule_sets"]["current"].update(duty_free_threshold_eur=100))
    assert load_tax_rates(p).parcel["current"].duty_free_threshold_eur == D("100")


def test_alternative_file_via_env(tmp_path, monkeypatch):
    p = _write(tmp_path, lambda r: r.update(version="test-version"))
    monkeypatch.setenv("TAX_RATES_PATH", str(p))
    assert load_tax_rates().version == "test-version"


@pytest.mark.parametrize("mutate", [
    lambda r: r["parcel_rule_sets"].pop("july_2027"),
    lambda r: r["car_rule_sets"]["current"].update(hybrid_excise_as="steam"),
    lambda r: r["parcel_rule_sets"]["current"]["sources"].append("no_such_source"),
    lambda r: r["car_rule_sets"]["current"].pop("vat_rate"),
])
def test_broken_file_fails_loudly(tmp_path, mutate):
    with pytest.raises((ValueError, KeyError)):
        load_tax_rates(_write(tmp_path, mutate))
