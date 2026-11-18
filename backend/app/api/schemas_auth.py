from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationInfo, field_validator


class SignUpIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    # The sign-up form asks for the password twice. Compared exactly (no trimming, case-sensitive),
    # so a typo cannot create an account the user then cannot sign in to.
    password_confirm: str
    name: str | None = Field(default=None, max_length=100)

    @field_validator("password_confirm")
    @classmethod
    def _passwords_match(cls, v: str, info: ValidationInfo) -> str:
        password = info.data.get("password")  # absent if the password itself failed validation
        if password is not None and v != password:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("name")
    @classmethod
    def _blank_name_is_none(cls, v: str | None) -> str | None:
        return v.strip() or None if v is not None else None


class SignInIn(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthIn(BaseModel):
    credential: str = Field(min_length=1)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
