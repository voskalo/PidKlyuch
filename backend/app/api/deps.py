"""Shared FastAPI dependencies (current user resolution)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User

_bearer = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _user_from_token(token: str, db: Session) -> User | None:
    user_id = decode_access_token(token)
    return db.get(User, user_id) if user_id is not None else None


def get_optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """No token -> anonymous (None). A token that is invalid/expired -> 401, so the client signs the user
    out instead of silently losing the calculation from their history."""
    if creds is None:
        return None
    user = _user_from_token(creds.credentials, db)
    if user is None:
        raise _unauthorized()
    return user


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    user = _user_from_token(creds.credentials, db) if creds else None
    if user is None:
        raise _unauthorized()
    return user
