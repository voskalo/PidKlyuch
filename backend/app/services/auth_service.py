"""Account use cases: register and authenticate users."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User


class EmailAlreadyRegistered(Exception):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def _by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(func.lower(User.email) == email.lower()))

    def register(self, email: str, password: str, name: str | None) -> User:
        if self._by_email(email):
            raise EmailAlreadyRegistered(email)
        user = User(email=email.lower(), name=name, password_hash=hash_password(password))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return user
