PARCEL = {"delivery_type": "parcel", "category": "electronics", "item_price": 200,
          "shipping_price": 15, "currency": "EUR"}
CAR = {"delivery_type": "car", "car_price": 10000, "shipping_price": 0, "currency": "EUR",
       "engine_type": "petrol", "engine_volume_cc": 2000, "manufacture_year": 2014, "origin": "other"}


def test_calculate_parcel(client):
    r = client.post("/api/calculate", json=PARCEL)
    assert r.status_code == 200
    b = r.json()
    assert b["taxes_total_eur"] == "16.00"
    assert b["taxes_total_uah"] == "800.00"  # 16 × 50
    assert b["landed_total_eur"] == "231.00"
    assert [l["code"] for l in b["lines"]] == ["duty", "vat"]
    assert b["calculation_id"] is None
    assert b["rate_source"] == "nbu"


def test_calculate_parcel_in_usd_is_converted(client):
    r = client.post("/api/calculate", json={**PARCEL, "item_price": 250, "shipping_price": 0, "currency": "USD"})
    b = r.json()
    assert b["goods_value_eur"] == "200.00"  # 250 USD × 40 / 50
    assert b["taxes_total_eur"] == "16.00"
    assert any("НБУ" in n for n in b["notes"])


def test_calculate_car(client):
    r = client.post("/api/calculate", json=CAR)
    assert r.status_code == 200
    assert [l["code"] for l in r.json()["lines"]] == ["duty", "excise", "vat"]


def test_car_is_new_field(client):
    big = {**CAR, "engine_volume_cc": 3500, "manufacture_year": 2024}
    used = client.post("/api/calculate", json=big).json()
    new = client.post("/api/calculate", json={**big, "is_new": True}).json()
    duty = lambda b: next(l for l in b["lines"] if l["code"] == "duty")
    assert duty(used)["amount_eur"] == "1000.00"
    assert duty(new)["amount_eur"] == "500.00"
    assert "нове бензинове авто понад 3000 см³" in duty(new)["formula"]


def test_car_validation(client):
    bad = {**CAR, "engine_volume_cc": None}
    assert client.post("/api/calculate", json=bad).status_code == 422
    ev = {**CAR, "engine_type": "electric", "engine_volume_cc": None}
    assert client.post("/api/calculate", json=ev).status_code == 422
    assert client.post("/api/calculate", json={**ev, "battery_kwh": 60}).status_code == 200


def test_bad_input(client):
    assert client.post("/api/calculate", json={**PARCEL, "item_price": -5}).status_code == 422
    assert client.post("/api/calculate", json={**PARCEL, "currency": "BTC"}).status_code == 422
    assert client.post("/api/calculate", json={**PARCEL, "delivery_type": "boat"}).status_code == 422


def test_compare_rules(client):
    r = client.post("/api/calculate/compare-rules", json={**PARCEL, "item_price": 40})
    assert r.status_code == 200
    b = r.json()
    assert b["current"]["taxes_total_eur"] == "0.00"
    assert b["july_2027"]["taxes_total_eur"] == "8.00"
    gift = client.post("/api/calculate/compare-rules", json={**PARCEL, "item_price": 40, "sender": "private"})
    assert gift.json()["july_2027"]["taxes_total_eur"] == "0.00"


def test_response_says_which_rates_were_used(client):
    b = client.post("/api/calculate", json=PARCEL).json()
    assert b["rates_verified_at"] == "2026-11-18"
    assert b["rates_version"]
