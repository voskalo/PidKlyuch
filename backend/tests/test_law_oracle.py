"""Differential test: the customs law written a SECOND time, straight from the statutes, without reading
tax_rates.json or the engine, compared with the real API on 1000 seeded random + boundary inputs.

If you change a rate in tax_rates.json on purpose, change the matching number in the oracle below too
(that double bookkeeping is the point: a typo in one place fails the test).
Sources: MK 374 p.7, TC 191.1.1, Laws 5025-IX/5026-IX, TC 215.3.5-1, Customs Tariff 8703 (see AGENTS.md §13).
"""
import random
from datetime import date
from decimal import ROUND_HALF_UP, Decimal as D

from app.main import app
from app.services.rates_service import RatesService, get_rates_service

# Awkward real-looking rates (not round numbers) so currency rounding is exercised.
NBU = [
    {"cc": "EUR", "rate": 50.3127, "exchangedate": "18.11.2026"},
    {"cc": "USD", "rate": 41.4011, "exchangedate": "18.11.2026"},
    {"cc": "GBP", "rate": 57.0099, "exchangedate": "18.11.2026"},
    {"cc": "PLN", "rate": 11.7713, "exchangedate": "18.11.2026"},
]
UAH = {"UAH": D(1), **{r["cc"]: D(str(r["rate"])) for r in NBU}}
Y = date.today().year


def c(x: D) -> D:
    return x.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def eur(amount: D, cur: str) -> D:
    return c(amount * UAH[cur] / UAH["EUR"])


# ---------------- the law, written again from the statute text ----------------
def oracle_parcel(g: D, rules: str, sender: str) -> dict:
    out = {}
    if rules == "current":  # MK 374 p.7 + TC 191.1.1
        if g > 150:
            ex = g - 150
            out["duty"] = c(ex * D("0.10"))
            out["vat"] = c((ex + out["duty"]) * D("0.20"))
    else:  # Laws 5025-IX / 5026-IX
        if g > 150:
            out["duty"] = c(g * D("0.10"))
            out["vat"] = c((g + out["duty"]) * D("0.20"))
        elif sender == "private" and g <= 45:
            pass
        elif g > 0:
            out["vat"] = c(g * D("0.20"))
    return out


def oracle_car(price, ship, engine, cc, kwh, year, origin, is_new) -> dict:
    cv = price + ship
    new = is_new if is_new is not None else year >= Y
    if engine == "electric" or origin == "eu":
        rate = D(0)
    elif engine in ("petrol", "hybrid") and cc > 3000 and new:
        rate = D("0.05")
    else:
        rate = D("0.10")
    duty = c(cv * rate)
    if engine == "electric":
        excise = c(D(str(kwh)) * 1)
    else:
        k = 1 if new else max(1, min(15, Y - year - 1))  # TC 215.3.5-1: new car -> 1
        if engine == "diesel":
            base = D(75) if cc <= 3500 else D(150)
        else:
            base = D(50) if cc <= 3000 else D(100)
        excise = c(base * D(cc) / 1000 * k)
    vat = c((cv + duty + excise) * D("0.20"))
    return {"duty": duty, "excise": excise, "vat": vat}


# ---------------- random input generators with boundary bias ----------------
PARCEL_EDGES = ["0", "0.01", "44.99", "45", "45.00", "45.01", "100", "149.99", "150", "150.00", "150.01",
                "150.05", "151", "199.99", "200", "999.99", "1000", "9999.99", "10000", "10000.01", "123456.78"]
CCS = [1, 600, 999, 1000, 1598, 1998, 2999, 3000, 3001, 3499, 3500, 3501, 4400, 6200, 10000]
YEARS = [1950, 1980, 2000, Y - 16, Y - 15, Y - 14, Y - 3, Y - 2, Y - 1, Y, Y + 1]


def rnd_amount(r: random.Random, edges) -> str:
    if r.random() < 0.4:
        return r.choice(edges)
    return f"{D(r.randint(0, 2_000_000)) / 100:.2f}"


def gen_parcel(r):
    cur = r.choice(["EUR", "EUR", "USD", "UAH", "GBP", "PLN"])
    price = rnd_amount(r, PARCEL_EDGES)
    if cur == "UAH" and r.random() < 0.5:  # amounts close to the threshold after conversion
        price = f"{c(D(r.choice(['45', '150'])) * UAH['EUR'] + D(r.randint(-3, 3)) / 100):.2f}"
    body = {"delivery_type": "parcel", "item_price": price, "currency": cur,
            "category": r.choice(["electronics", "clothing", "cosmetics", "toys", "other"])}
    if r.random() < 0.8:
        body["shipping_price"] = rnd_amount(r, ["0", "5", "15", "20.5"])
    if r.random() < 0.8:
        body["rules"] = r.choice(["current", "july_2027"])
    if r.random() < 0.8:
        body["sender"] = r.choice(["marketplace", "private"])
    return body


def gen_car(r):
    engine = r.choice(["petrol", "diesel", "hybrid", "electric"])
    body = {"delivery_type": "car", "car_price": rnd_amount(r, ["1", "5000", "10000", "50000", "250000.55"]),
            "currency": r.choice(["EUR", "USD", "UAH", "GBP", "PLN"]), "engine_type": engine,
            "manufacture_year": r.choice(YEARS) if r.random() < 0.6 else r.randint(1950, Y + 1)}
    if r.random() < 0.8:
        body["shipping_price"] = rnd_amount(r, ["0", "800", "1200"])
    if r.random() < 0.8:
        body["origin"] = r.choice(["eu", "other"])
    if r.random() < 0.6:
        body["is_new"] = r.choice([True, False, None])
    if engine == "electric":
        body["battery_kwh"] = r.choice(["1", "40", "75.5", "100", "500"])
        if r.random() < 0.3:
            body["engine_volume_cc"] = r.choice(CCS)  # must be ignored
    else:
        body["engine_volume_cc"] = r.choice(CCS) if r.random() < 0.7 else r.randint(1, 10000)
    return body


def expected(body):
    cur = body.get("currency", "EUR")
    ship = eur(D(body.get("shipping_price", "0")), cur)
    if body["delivery_type"] == "parcel":
        g = eur(D(body["item_price"]), cur)
        return g, ship, oracle_parcel(g, body.get("rules", "current"), body.get("sender", "marketplace"))
    price = eur(D(body["car_price"]), cur)
    return price, ship, oracle_car(price, ship, body["engine_type"], body.get("engine_volume_cc"),
                                   body.get("battery_kwh"), body["manufacture_year"], body.get("origin", "other"),
                                   body.get("is_new"))


def test_engine_matches_independent_oracle(client):
    app.dependency_overrides[get_rates_service] = lambda: RatesService(fetcher=lambda: NBU)
    r = random.Random(20261118)
    seen = set()
    mismatches = []
    for _ in range(1000):
        body = gen_parcel(r) if r.random() < 0.5 else gen_car(r)
        res = client.post("/api/calculate", json=body)
        assert res.status_code == 200, (body, res.text)
        js = res.json()
        g, ship, exp = expected(body)
        tax = c(sum(exp.values(), D(0)))
        got = {line["code"]: D(line["amount_eur"]) for line in js["lines"]}
        ok = (D(js["goods_value_eur"]) == g and D(js["shipping_eur"]) == ship and got == exp
              and D(js["taxes_total_eur"]) == tax and D(js["landed_total_eur"]) == c(g + ship + tax)
              and D(js["taxes_total_uah"]) == c(tax * UAH["EUR"])
              and all(line["amount_eur"] in line["formula"] for line in js["lines"]))
        if not ok:
            mismatches.append((body, js["lines"], exp))
        seen.add(body["delivery_type"] + ":" + ",".join(sorted(exp)))
    assert not mismatches, mismatches[:3]
    # every branch was exercised: tax-free, VAT-only (2027), duty+VAT parcels, and cars
    assert seen == {"parcel:", "parcel:vat", "parcel:duty,vat", "car:duty,excise,vat"}, seen
