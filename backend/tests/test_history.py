from datetime import datetime, timedelta, timezone

from app.core.database import SessionLocal, normalize_db_url
from app.models import Calculation
from tests.test_calculate_api import CAR, PARCEL


def _auth(client, email="h@example.com"):
    r = client.post("/api/auth/signup", json={"email": email, "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_signed_in_calculation_is_saved_and_listed(client):
    h = _auth(client)
    r1 = client.post("/api/calculate", json=PARCEL, headers=h)
    r2 = client.post("/api/calculate", json=CAR, headers=h)
    assert r1.json()["calculation_id"] is not None

    items = client.get("/api/history", headers=h).json()
    assert [i["id"] for i in items] == [r2.json()["calculation_id"], r1.json()["calculation_id"]]
    assert items[1]["input"]["item_price"] == "200"
    assert items[1]["result"]["taxes_total_eur"] == "16.00"


def test_history_is_private_and_requires_auth(client):
    a, b = _auth(client, "a@example.com"), _auth(client, "b@example.com")
    calc_id = client.post("/api/calculate", json=PARCEL, headers=a).json()["calculation_id"]
    assert client.get("/api/history").status_code == 401
    assert client.get("/api/history", headers=b).json() == []
    assert client.delete(f"/api/history/{calc_id}", headers=b).status_code == 404
    assert client.delete(f"/api/history/{calc_id}", headers=a).status_code == 204
    assert client.get("/api/history", headers=a).json() == []


def test_stats(client):
    h = _auth(client)
    client.post("/api/calculate", json=PARCEL)  # anonymous
    client.post("/api/calculate", json=PARCEL, headers=h)
    client.post("/api/calculate", json=CAR, headers=h)
    s = client.get("/api/stats").json()
    assert s == {"users": 1, "calculations": 3, "calculations_by_signed_in": 2, "returning_users": 0}

    # Same user calculating on another day counts as returning
    with SessionLocal() as db:
        calc = db.query(Calculation).filter(Calculation.user_id.is_not(None)).first()
        calc.created_at = datetime.now(timezone.utc) - timedelta(days=3)
        db.commit()
    assert client.get("/api/stats").json()["returning_users"] == 1


def test_normalize_db_url():
    assert normalize_db_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_db_url("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_db_url("sqlite:///./x.db") == "sqlite:///./x.db"
