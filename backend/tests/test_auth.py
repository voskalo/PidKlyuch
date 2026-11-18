import pytest
from google.oauth2 import id_token

from app.core.config import get_settings
from app.core.security import hash_password, verify_password


def _signup(client, email="user@example.com", password="secret123", name="Test", password_confirm=None):
    confirm = password if password_confirm is None else password_confirm
    return client.post("/api/auth/signup",
                       json={"email": email, "password": password, "password_confirm": confirm, "name": name})


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


def test_google_auth_auto_registers_new_user(client, monkeypatch):
    def fake_verify(token, request, audience=None):
        assert token == "valid-google-token"
        return {
            "sub": "google-sub-123",
            "email": "GoogleUser@Example.com",
            "email_verified": True,
            "name": "Google User",
            "iss": "https://accounts.google.com",
        }

    monkeypatch.setattr(id_token, "verify_oauth2_token", fake_verify)

    r = client.post("/api/auth/google", json={"credential": "valid-google-token"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "googleuser@example.com"
    assert body["user"]["name"] == "Google User"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["id"] == body["user"]["id"]

    # OAuth-only accounts cannot sign in with password
    pw_attempt = client.post(
        "/api/auth/signin", json={"email": "googleuser@example.com", "password": "any-password"}
    )
    assert pw_attempt.status_code == 401


def test_google_auth_links_existing_user_by_email(client, monkeypatch):
    created = _signup(client, email="existing@example.com", password="secret123", name=None).json()
    existing_id = created["user"]["id"]

    monkeypatch.setattr(
        id_token,
        "verify_oauth2_token",
        lambda token, req, audience=None: {
            "sub": "google-sub-456",
            "email": "existing@example.com",
            "email_verified": True,
            "name": "Linked Name",
            "iss": "accounts.google.com",
        },
    )

    r = client.post("/api/auth/google", json={"credential": "link-token"})
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["id"] == existing_id
    assert body["user"]["name"] == "Linked Name"

    # Existing password login continues to work
    pw_signin = client.post(
        "/api/auth/signin", json={"email": "existing@example.com", "password": "secret123"}
    )
    assert pw_signin.status_code == 200


def test_google_auth_invalid_token_returns_401(client, monkeypatch):
    def fake_verify(token, request, audience=None):
        raise ValueError("Token signature invalid")

    monkeypatch.setattr(id_token, "verify_oauth2_token", fake_verify)

    r = client.post("/api/auth/google", json={"credential": "bad-token"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid Google token"


def test_google_auth_unverified_email_and_audience(client, monkeypatch):
    seen_audiences = []
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "12345.apps.googleusercontent.com")
    get_settings.cache_clear()
    try:
        def fake_verify(token, request, audience=None):
            seen_audiences.append(audience)
            return {
                "sub": "sub-unverified",
                "email": "unverified@example.com",
                "email_verified": False,
            }

        monkeypatch.setattr(id_token, "verify_oauth2_token", fake_verify)
        r = client.post("/api/auth/google", json={"credential": "some-token"})
        assert r.status_code == 401
        assert seen_audiences == ["12345.apps.googleusercontent.com"]
    finally:
        monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
        get_settings.cache_clear()


# --- Password typed twice on sign-up (password_confirm) ----------------------------------------

def _confirm_errors(r):
    return [e for e in r.json()["detail"] if e["loc"][-1] == "password_confirm"]


@pytest.mark.parametrize("confirm", [
    "secret124",      # one character off
    "Secret123",      # case differs
    "secret123 ",     # trailing space (not trimmed)
    " secret123",     # leading space
    "",               # left empty
])
def test_signup_rejects_mismatched_confirmation_and_creates_no_user(client, confirm):
    r = _signup(client, password="secret123", password_confirm=confirm)
    assert r.status_code == 422
    errors = _confirm_errors(r)
    assert len(errors) == 1 and "Passwords do not match" in errors[0]["msg"]
    # nothing was created: the same email can still sign up, and cannot sign in
    assert client.post("/api/auth/signin", json={"email": "user@example.com", "password": "secret123"}).status_code == 401
    assert _signup(client).status_code == 201


def test_signup_requires_the_confirmation_field(client):
    r = client.post("/api/auth/signup", json={"email": "user@example.com", "password": "secret123"})
    assert r.status_code == 422
    assert [e["type"] for e in _confirm_errors(r)] == ["missing"]


def test_too_short_password_reports_only_the_length_problem(client):
    r = _signup(client, password="short", password_confirm="other")
    assert r.status_code == 422
    assert [e["loc"][-1] for e in r.json()["detail"]] == ["password"]


def test_matching_confirmation_signs_up_and_password_works(client):
    pw = "Пароль з пробілом 🔑"
    assert _signup(client, password=pw, password_confirm=pw).status_code == 201
    assert client.post("/api/auth/signin", json={"email": "user@example.com", "password": pw}).status_code == 200


def test_signin_does_not_need_confirmation(client):
    _signup(client)
    r = client.post("/api/auth/signin", json={"email": "user@example.com", "password": "secret123"})
    assert r.status_code == 200
