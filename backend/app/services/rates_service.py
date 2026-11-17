"""NBU (National Bank of Ukraine) exchange rates with in-memory caching and a static fallback."""
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

import httpx

from app.core.config import get_settings

log = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = ("EUR", "USD", "UAH", "GBP", "PLN")

# Approximate UAH rates (NBU, 16.11.2026), used ONLY when the NBU API is unreachable and nothing is cached.
FALLBACK_UAH_PER_UNIT: dict[str, Decimal] = {
    "EUR": Decimal("50.22"),
    "USD": Decimal("45.43"),
    "GBP": Decimal("60.11"),
    "PLN": Decimal("11.39"),
}


@dataclass(frozen=True)
class RateTable:
    date: date
    source: str  # "nbu" | "fallback"
    uah_per_unit: dict[str, Decimal]  # always contains UAH = 1

    def to_eur(self, amount: Decimal, currency: str) -> Decimal:
        return amount * self.uah_per_unit[currency] / self.uah_per_unit["EUR"]

    def eur_to_uah(self, amount_eur: Decimal) -> Decimal:
        return amount_eur * self.uah_per_unit["EUR"]


def fetch_nbu_json() -> list[dict]:
    resp = httpx.get(get_settings().nbu_api_url, timeout=5.0)
    resp.raise_for_status()
    return resp.json()


def parse_nbu(payload: list[dict]) -> RateTable:
    rates: dict[str, Decimal] = {"UAH": Decimal("1")}
    rate_date = date.today()
    for row in payload:
        cc = row.get("cc")
        if cc in SUPPORTED_CURRENCIES:
            rates[cc] = Decimal(str(row["rate"]))
            if row.get("exchangedate"):
                rate_date = datetime.strptime(row["exchangedate"], "%d.%m.%Y").date()
    missing = set(SUPPORTED_CURRENCIES) - rates.keys()
    if missing:
        raise ValueError(f"NBU response missing currencies: {sorted(missing)}")
    return RateTable(date=rate_date, source="nbu", uah_per_unit=rates)


class RatesService:
    """Returns today's rates. Refetches at most every `ttl_seconds`; falls back gracefully."""

    def __init__(self, fetcher: Callable[[], list[dict]] = fetch_nbu_json, ttl_seconds: int = 3600):
        self._fetcher = fetcher
        self._ttl = ttl_seconds
        self._cached: RateTable | None = None
        self._fetched_at = 0.0

    def get_rates(self) -> RateTable:
        fresh = self._cached and time.monotonic() - self._fetched_at < self._ttl
        if fresh:
            return self._cached
        try:
            self._cached = parse_nbu(self._fetcher())
            self._fetched_at = time.monotonic()
        except Exception as exc:  # network errors, bad JSON, missing currencies
            log.warning("NBU rates unavailable, using %s: %s", "cache" if self._cached else "fallback", exc)
            if self._cached is None:
                return RateTable(
                    date=date.today(),
                    source="fallback",
                    uah_per_unit={"UAH": Decimal("1"), **FALLBACK_UAH_PER_UNIT},
                )
        return self._cached


_rates_service = RatesService()


def get_rates_service() -> RatesService:
    """FastAPI dependency (overridden in tests)."""
    return _rates_service
