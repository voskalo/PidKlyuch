from decimal import Decimal as D

from app.services.rates_service import RatesService
from tests.conftest import FAKE_NBU


def test_parses_nbu_and_converts():
    t = RatesService(fetcher=lambda: FAKE_NBU).get_rates()
    assert t.source == "nbu"
    assert str(t.date) == "2026-11-16"
    assert t.uah_per_unit["UAH"] == D("1")
    assert t.to_eur(D("100"), "USD") == D("80")  # 100 USD = 4000 UAH = 80 EUR
    assert t.to_eur(D("500"), "UAH") == D("10")


def test_fallback_when_api_down():
    def boom():
        raise ConnectionError("no network")

    t = RatesService(fetcher=boom).get_rates()
    assert t.source == "fallback"
    assert t.uah_per_unit["EUR"] > 0


def test_keeps_last_good_rates_when_api_fails_later():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] > 1:
            raise ConnectionError
        return FAKE_NBU

    svc = RatesService(fetcher=flaky, ttl_seconds=0)
    assert svc.get_rates().source == "nbu"
    assert svc.get_rates().source == "nbu"  # refetch failed, cache served
    assert calls["n"] == 2


def test_rates_endpoint(client):
    r = client.get("/api/rates")
    assert r.status_code == 200
    assert r.json()["uah_per_unit"]["EUR"] == "50.0"
