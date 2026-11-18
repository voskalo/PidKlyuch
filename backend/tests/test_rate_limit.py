"""Sign-in brute-force protection (app/core/rate_limit.py, POST /api/auth/signin)."""
from app.core.rate_limit import LoginRateLimiter

PW = "secret123"


def signup(client, email="victim@example.com"):
    return client.post("/api/auth/signup", json={"email": email, "password": PW, "password_confirm": PW})


def signin(client, email="victim@example.com", password="wrongpass1", ip=None):
    headers = {"X-Forwarded-For": ip} if ip else {}
    return client.post("/api/auth/signin", json={"email": email, "password": password}, headers=headers)


def test_account_is_locked_after_5_failures_even_for_the_right_password(client):
    signup(client)
    assert [signin(client).status_code for _ in range(5)] == [401] * 5
    r = signin(client)
    assert r.status_code == 429
    assert 0 < int(r.headers["Retry-After"]) <= 900
    assert r.json()["detail"] == "Too many sign-in attempts, try again later"
    assert signin(client, password=PW).status_code == 429  # locked: the correct password does not get through


def test_a_successful_sign_in_resets_the_account_counter(client):
    signup(client)
    for _ in range(4):
        assert signin(client).status_code == 401
    assert signin(client, password=PW).status_code == 200
    assert [signin(client).status_code for _ in range(4)] == [401] * 4  # counting starts again


def test_other_accounts_are_not_locked_by_one_account(client):
    signup(client)
    signup(client, "other@example.com")
    for _ in range(5):
        signin(client)
    assert signin(client, "other@example.com", PW).status_code == 200


def test_ip_limit_stops_password_spraying_across_accounts(client):
    codes = [signin(client, f"user{i}@example.com").status_code for i in range(20)]
    assert codes == [401] * 20
    assert signin(client, "fresh@example.com").status_code == 429


def test_email_case_and_spaces_count_as_the_same_account(client):
    for email in ("Victim@Example.com", "VICTIM@example.com", " victim@example.com", "victim@EXAMPLE.com", "victim@example.com"):
        signin(client, email)
    assert signin(client).status_code == 429


def test_failures_expire_after_the_window():
    now = [1000.0]
    limiter = LoginRateLimiter(max_per_account=2, max_per_ip=100, window_seconds=60, clock=lambda: now[0])
    limiter.record_failure("1.1.1.1", "a@b.c")
    now[0] += 10
    limiter.record_failure("1.1.1.1", "a@b.c")
    assert limiter.blocked_for("1.1.1.1", "a@b.c") == 50  # until the first failure is 60 s old
    now[0] += 50
    assert limiter.blocked_for("1.1.1.1", "a@b.c") == 0
    assert limiter.blocked_for("2.2.2.2", "x@y.z") == 0


def test_signup_and_other_endpoints_are_not_rate_limited(client):
    for _ in range(6):
        signin(client)
    assert signup(client, "new@example.com").status_code == 201
    assert client.get("/api/health").status_code == 200
