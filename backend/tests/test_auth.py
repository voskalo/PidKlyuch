from app.core.security import hash_password, verify_password


def _signup(client, email="user@example.com", password="secret123", name="Test"):
    return client.post("/api/auth/signup", json={"email": email, "password": password, "name": name})


def test_password_hash_roundtrip():
    h = hash_password("hunter22")
    assert verify_password("hunter22", h)
    assert not verify_password("wrong", h)
    assert not verify_password("hunter22", "garbage")


def test_signup_returns_token_and_user(client):
    r = _signup(client)
    assert r.status_code == 201
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "user@example.com"
    assert "password_hash" not in body["user"]


def test_signup_duplicate_email_case_insensitive(client):
    _signup(client)
    r = _signup(client, email="USER@example.com")
    assert r.status_code == 409


def test_signup_validates_input(client):
    assert _signup(client, password="short").status_code == 422
    assert _signup(client, email="not-an-email").status_code == 422


def test_signin_and_me(client):
    _signup(client)
    r = client.post("/api/auth/signin", json={"email": "user@example.com", "password": "secret123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"


def test_signin_wrong_password(client):
    _signup(client)
    r = client.post("/api/auth/signin", json={"email": "user@example.com", "password": "nope-nope"})
    assert r.status_code == 401


def test_me_requires_valid_token(client):
    assert client.get("/api/auth/me").status_code == 401
    bad = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert bad.status_code == 401
