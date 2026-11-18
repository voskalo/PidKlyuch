from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas_auth import GoogleAuthIn, SignInIn, SignUpIn, TokenOut, UserOut
from app.core.database import get_db
from app.core.rate_limit import LoginRateLimiter, get_login_limiter
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


@router.post("/signin", response_model=TokenOut, responses={429: {"description": "Too many failed sign-in attempts"}})
def signin(
    body: SignInIn,
    request: Request,
    db: Session = Depends(get_db),
    limiter: LoginRateLimiter = Depends(get_login_limiter),
) -> TokenOut:
    # Behind Caddy, uvicorn --proxy-headers puts the real client IP (X-Forwarded-For) in request.client
    ip = request.client.host if request.client else "unknown"
    email = str(body.email).strip().lower()
    wait = limiter.blocked_for(ip, email)
    if wait:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many sign-in attempts, try again later",
                            headers={"Retry-After": str(wait)})
    user = AuthService(db).authenticate(body.email, body.password)
    if user is None:
        limiter.record_failure(ip, email)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    limiter.record_success(email)
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
