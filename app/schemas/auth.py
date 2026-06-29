from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserSessionCreate(BaseModel):
    user_id: str
    session_id: str
    expires_at: datetime
    device_name: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None


class UserSessionResponse(BaseModel):
    id: UUID  # ORM uses UUID(as_uuid=True) — was incorrectly typed as int
    user_id: str
    session_id: str
    device_name: str | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    revoked_at: datetime | None = None
    expires_at: datetime | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    csrf_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str = "Successfully logged out"


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class SignupResponse(BaseModel):
    message: str = "Successfully signed up"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class ResetPasswordResponse(BaseModel):
    message: str = "Successfully reset password"


class AddUserToken(BaseModel):
    jti: str
    user_id: str
    session_id: str | None = None  # nullable — password reset tokens have no session
    token_type: str
    expires_at: datetime


class AddUserTokenResponse(BaseModel):
    jti: str
    user_id: str
    session_id: str | None = None
    token_type: str
    expires_at: datetime
    revoked_at: datetime
