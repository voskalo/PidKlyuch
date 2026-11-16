import os

# Configure the app for tests BEFORE importing it.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["PASSWORD_HASH_ITERATIONS"] = "1000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.rates_service import RatesService, get_rates_service  # noqa: E402

# Fake NBU payload: 1 EUR = 50 UAH, 1 USD = 40 UAH (easy mental math in tests)
FAKE_NBU = [
    {"cc": "EUR", "rate": 50.0, "exchangedate": "16.11.2026"},
    {"cc": "USD", "rate": 40.0, "exchangedate": "16.11.2026"},
    {"cc": "GBP", "rate": 60.0, "exchangedate": "16.11.2026"},
    {"cc": "PLN", "rate": 12.5, "exchangedate": "16.11.2026"},
]


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides[get_rates_service] = lambda: RatesService(fetcher=lambda: FAKE_NBU)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
