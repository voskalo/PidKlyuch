"""Account use cases: register and authenticate users."""
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models import User


class EmailAlreadyRegistered(Exception):
    pass


class InvalidGoogleToken(Exception):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def _by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(func.lower(User.email) == email.lower()))

    def _by_google_sub(self, google_sub: str) -> User | None:
        return self.db.scalar(select(User).where(User.google_sub == google_sub))

    def register(self, email: str, password: str, name: str | None) -> User:
        if self._by_email(email):
            raise EmailAlreadyRegistered(email)
        user = User(email=email.lower(), name=name, password_hash=hash_password(password))
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:  # another request registered the same email in between
            self.db.rollback()
            raise EmailAlreadyRegistered(email)
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return user

    def authenticate_google(self, credential: str) -> User:
        audience = get_settings().GOOGLE_CLIENT_ID or None
        try:
            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                audience,
            )
        except Exception as exc:
            raise InvalidGoogleToken("Invalid Google token") from exc

        if not isinstance(idinfo, dict):
            raise InvalidGoogleToken("Invalid Google token")
        if "iss" in idinfo and idinfo["iss"] not in ("accounts.google.com", "https://accounts.google.com"):
            raise InvalidGoogleToken("Invalid Google token issuer")
        if idinfo.get("email_verified") is False:
            raise InvalidGoogleToken("Google email is not verified")

        email = str(idinfo.get("email") or "").strip().lower()
        if not email:
            raise InvalidGoogleToken("Google token missing email")

        sub = str(idinfo.get("sub") or "").strip()
        raw_name = idinfo.get("name")
        name = (str(raw_name).strip()[:100] or None) if raw_name is not None else None

        user = self._by_google_sub(sub) if sub else None
        if user is None:
            user = self._by_email(email)

        if user is not None:
            changed = False
            if sub and not user.google_sub:
                user.google_sub = sub
                changed = True
            if name and not user.name:
                user.name = name
                changed = True
            if changed:
                self.db.commit()
                self.db.refresh(user)
            return user

        user = User(
            email=email,
            name=name,
            password_hash="!oauth",
            google_sub=sub or None,
            auth_provider="google",
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = (self._by_google_sub(sub) if sub else None) or self._by_email(email)
            if existing is not None:
                return existing
            raise
        self.db.refresh(user)
        return user
