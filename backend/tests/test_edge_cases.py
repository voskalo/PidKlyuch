"""Edge cases found by probing the API on 17.11.2026 (regressions + hostile/boundary input)."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.services.auth_service import AuthService, EmailAlreadyRegistered
from tests.test_calculate_api import CAR, PARCEL


def signup(client, email="edge@example.com", **extra):
    return client.post("/api/auth/signup", json={"email": email, "password": "secret123",
                                                  "password_confirm": "secret123", **extra})


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def token_for(client, email="edge@example.com"):
    return signup(client, email).json()["access_token"]


# --- Bug 1: car validation errors must be about the car, not "should be 'parcel'" -------------

@pytest.mark.parametrize("bad,field", [
    ({"engine_volume_cc": 0}, "engine_volume_cc"),
    ({"engine_volume_cc": 1998.5}, "engine_volume_cc"),
    ({"origin": "usa"}, "origin"),
    ({"manufacture_year": 1949}, "manufacture_year"),
    ({"engine_type": "electric", "battery_kwh": 0}, "battery_kwh"),
])
def test_car_errors_point_at_the_car_field(client, bad, field):
    r = client.post("/api/calculate", json={**CAR, **bad})
    assert r.status_code == 422
    errors = r.json()["detail"]
    assert all("'parcel'" not in e["msg"] for e in errors), errors
    assert errors[0]["loc"][-1] == field


def test_missing_engine_data_message_is_first(client):
    r = client.post("/api/calculate", json={**CAR, "engine_volume_cc": None})
    assert r.status_code == 422
    assert "engine_volume_cc is required" in r.json()["detail"][0]["msg"]


def test_unknown_delivery_type_is_rejected_clearly(client):
    r = client.post("/api/calculate", json={**PARCEL, "delivery_type": "boat"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] == "union_tag_invalid"


# --- Bug 2: a present-but-invalid token must be 401, not silently anonymous -----------------

def test_invalid_token_on_calculate_is_401_not_anonymous(client):
    r = client.post("/api/calculate", json=PARCEL, headers=bearer("garbage"))
    assert r.status_code == 401
    assert client.get("/api/stats").json()["calculations"] == 0  # nothing stored


def test_no_token_on_calculate_is_still_allowed(client):
    r = client.post("/api/calculate", json=PARCEL)
    assert r.status_code == 200 and r.json()["calculation_id"] is None


def _token(payload, secret="test-secret", alg="HS256"):
    return jwt.encode(payload, secret, algorithm=alg)


@pytest.mark.parametrize("make", [
    lambda: _token({"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}),  # expired
    lambda: _token({"sub": "1"}, secret="wrong-secret"),  # forged signature
    lambda: _token({"foo": "1"}),  # no subject
    lambda: _token({"sub": "abc"}),  # subject not an id
    lambda: _token({"sub": "9999"}),  # user does not exist
    lambda: jwt.encode({"sub": "1"}, None, algorithm="none"),  # unsigned token
])
def test_bad_tokens_are_rejected_everywhere(client, make):
    signup(client)  # user id 1 exists
    h = bearer(make())
    assert client.get("/api/auth/me", headers=h).status_code == 401
    assert client.get("/api/history", headers=h).status_code == 401
    assert client.post("/api/calculate", json=PARCEL, headers=h).status_code == 401


def test_wrong_auth_scheme_is_401(client):
    tok = token_for(client)
    assert client.get("/api/auth/me", headers={"Authorization": f"Basic {tok}"}).status_code == 401


# --- Bug 3: concurrent sign-ups with the same email -> 409, never 500 ---------------------

def test_signup_race_returns_conflict_not_500(client):
    from app.core.database import SessionLocal

    signup(client, "race@example.com")
    with SessionLocal() as db:
        service = AuthService(db)
        service._by_email = lambda email: None  # simulate: the other request has not committed yet
        with pytest.raises(EmailAlreadyRegistered):
            service.register("race@example.com", "secret123", None)
    assert signup(client, "race@example.com").status_code == 409


# --- Auth input boundaries -----------------------------------------------------------------

def test_email_is_trimmed_and_case_insensitive(client):
    assert signup(client, "  Mixed@Example.COM ").status_code == 201
    assert signup(client, "mixed@example.com").status_code == 409
    r = client.post("/api/auth/signin", json={"email": "MIXED@example.com", "password": "secret123"})
    assert r.status_code == 200 and r.json()["user"]["email"] == "mixed@example.com"


@pytest.mark.parametrize("password,status", [("1234567", 422), ("12345678", 201), ("x" * 128, 201), ("x" * 129, 422)])
def test_password_length_bounds(client, password, status):
    r = client.post("/api/auth/signup", json={"email": "len@example.com", "password": password,
                                                   "password_confirm": password})
    assert r.status_code == status


def test_unicode_password_roundtrip(client):
    pw = "пароль🔑пароль"
    assert client.post("/api/auth/signup", json={"email": "u@example.com", "password": pw,
                                                    "password_confirm": pw}).status_code == 201
    assert client.post("/api/auth/signin", json={"email": "u@example.com", "password": pw}).status_code == 200


@pytest.mark.parametrize("name,expected", [("", None), ("   ", None), ("  Анна  ", "Анна")])
def test_blank_name_becomes_null_and_is_trimmed(client, name, expected):
    assert signup(client, name=name).json()["user"]["name"] == expected


def test_name_too_long(client):
    assert signup(client, name="я" * 101).status_code == 422


def test_unknown_email_and_wrong_password_give_same_error(client):
    signup(client)
    a = client.post("/api/auth/signin", json={"email": "nobody@example.com", "password": "secret123"})
    b = client.post("/api/auth/signin", json={"email": "edge@example.com", "password": "wrong-pass"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()  # no hint whether the email exists


# --- Money input boundaries ----------------------------------------------------------------

@pytest.mark.parametrize("price", ["NaN", "Infinity", "-Infinity", "sNaN", True, -0.01, "150.005", 10_000_001, "abc"])
def test_invalid_prices_are_rejected(client, price):
    assert client.post("/api/calculate", json={**PARCEL, "item_price": price}).status_code == 422


@pytest.mark.parametrize("price", [0, "0.01", "1e3", 10_000_000, "199.99"])
def test_valid_prices_are_accepted(client, price):
    assert client.post("/api/calculate", json={**PARCEL, "item_price": price}).status_code == 200


def test_lowercase_currency_is_rejected(client):
    assert client.post("/api/calculate", json={**PARCEL, "currency": "eur"}).status_code == 422


@pytest.mark.parametrize("uah", ["7500.00", "7500.20"])  # €150.00 and €150.004 (rounds to €150.00) at 50 UAH/EUR
def test_threshold_after_currency_conversion_is_tax_free(client, uah):
    b = client.post("/api/calculate", json={**PARCEL, "item_price": uah, "shipping_price": 0, "currency": "UAH"}).json()
    assert b["goods_value_eur"] == "150.00"
    assert b["lines"] == []


def test_one_cent_over_threshold_after_conversion_is_taxed(client):
    # 7500.50 UAH = €150.01 -> duty 10% × 0.01 and VAT both round to 0.00, but the rule switches on
    b = client.post("/api/calculate", json={**PARCEL, "item_price": "7500.50", "shipping_price": 0, "currency": "UAH"}).json()
    assert b["goods_value_eur"] == "150.01"
    assert [l["code"] for l in b["lines"]] == ["duty", "vat"]
    assert b["taxes_total_eur"] == "0.00"


def test_parcel_at_max_value_gets_commercial_note(client):
    b = client.post("/api/calculate", json={**PARCEL, "item_price": 10_000_000}).json()
    assert "повне митне оформлення" in b["notes"][0]


def test_rejects_invalid_json_and_empty_body(client):
    assert client.post("/api/calculate").status_code == 422
    r = client.post("/api/calculate", content=b"{", headers={"content-type": "application/json"})
    assert r.status_code == 422


# --- Cars: year and engine boundaries ------------------------------------------------------

def test_next_model_year_is_allowed_with_age_coefficient_1(client):
    from datetime import date

    year = date.today().year + 1
    b = client.post("/api/calculate", json={**CAR, "manufacture_year": year}).json()
    assert "× 1 (коеф. віку)" in next(l for l in b["lines"] if l["code"] == "excise")["formula"]
    assert client.post("/api/calculate", json={**CAR, "manufacture_year": year + 1}).status_code == 422


def test_very_old_car_age_coefficient_capped_at_15(client):
    b = client.post("/api/calculate", json={**CAR, "manufacture_year": 1950}).json()
    assert "× 15 (коеф. віку)" in next(l for l in b["lines"] if l["code"] == "excise")["formula"]


def test_electric_ignores_engine_volume(client):
    ev = {**CAR, "engine_type": "electric", "battery_kwh": 60}  # engine_volume_cc still 2000
    lines = {l["code"]: l for l in client.post("/api/calculate", json=ev).json()["lines"]}
    assert lines["excise"]["amount_eur"] == "60.00"
    assert lines["duty"]["amount_eur"] == "0.00"


def test_compare_rules_rejects_car(client):
    assert client.post("/api/calculate/compare-rules", json=CAR).status_code == 422


# --- History & routing ---------------------------------------------------------------------

def test_cannot_delete_anonymous_or_foreign_or_bad_ids(client):
    client.post("/api/calculate", json=PARCEL)  # anonymous calc, id 1
    h = bearer(token_for(client))
    assert client.delete("/api/history/1", headers=h).status_code == 404
    assert client.delete("/api/history/-1", headers=h).status_code == 404
    assert client.delete("/api/history/abc", headers=h).status_code == 422


def test_history_returns_at_most_100(client):
    h = bearer(token_for(client))
    for _ in range(105):
        client.post("/api/calculate", json=PARCEL, headers=h)
    assert len(client.get("/api/history", headers=h).json()) == 100


def test_wrong_method_and_unknown_route(client):
    assert client.get("/api/calculate").status_code == 405
    assert client.get("/api/nope").status_code == 404


def test_cors_allows_frontend_dev_origin_only(client):
    pre = {"Access-Control-Request-Method": "POST"}
    ok = client.options("/api/calculate", headers={"Origin": "http://localhost:5173", **pre})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    evil = client.options("/api/calculate", headers={"Origin": "https://evil.example", **pre})
    assert "access-control-allow-origin" not in evil.headers
