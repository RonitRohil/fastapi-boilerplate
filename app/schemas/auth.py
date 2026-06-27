from pydantic import BaseModel, EmailStr


class UserSessionCreate(BaseModel):
    user_id: str
    session_id: str
    refresh_token: str | None = None
    csrf_token: str | None = None


class UserSessionResponse(BaseModel):
    id: int
    user_id: str
    session_id: str
    refresh_token: str | None = None
    csrf_token: str | None = None
    expires_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    csrf_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str
    csrf_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
    csrf_token: str


class LogoutResponse(BaseModel):
    message: str = "Successfully logged out"


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None


class SignupResponse(BaseModel):
    message: str = "Successfully signed up"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str = "Successfully reset password"
