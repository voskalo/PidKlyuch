from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas_auth import GoogleAuthIn, SignInIn, SignUpIn, TokenOut, UserOut
from app.core.database import get_db
from app.core.security import create_access_token
from app.models import User
from app.services.auth_service import AuthService, EmailAlreadyRegistered, InvalidGoogleToken

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user: User) -> TokenOut:
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def signup(body: SignUpIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        user = AuthService(db).register(body.email, body.password, body.name)
    except EmailAlreadyRegistered:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")
    return _token_response(user)


@router.post("/signin", response_model=TokenOut)
def signin(body: SignInIn, db: Session = Depends(get_db)) -> TokenOut:
    user = AuthService(db).authenticate(body.email, body.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return _token_response(user)


@router.post("/google", response_model=TokenOut)
def google_auth(body: GoogleAuthIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        user = AuthService(db).authenticate_google(body.credential)
    except InvalidGoogleToken:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
    return _token_response(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
