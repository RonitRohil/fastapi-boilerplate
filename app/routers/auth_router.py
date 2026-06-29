from fastapi import Cookie, Depends, HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.auth_service import (
    forgot_password_service,
    login_user,
    refresh_user_session,
    logout_user,
    signup_user,
    reset_password,
)
from app.core.dependencies import get_db, verify_csrf_token
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    SignupRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserResponse
from app.core.response import api_response
from app.core.config import settings
from app.core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])

# Refresh token cookie path — covers both /refresh and /logout
_REFRESH_COOKIE_PATH = "/api/v1/auth"


def _set_auth_cookies(
    response: JSONResponse, access_token: str, refresh_token: str, csrf_token: str
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=_REFRESH_COOKIE_PATH,
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # JS reads this and attaches it as X-CSRF-Token header
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/signup", status_code=201)
@limiter.limit("10/minute")
async def signup(
    sign_up_request: SignupRequest,
    request: Request,
    db=Depends(get_db),
):
    try:
        result = await signup_user(db, sign_up_request, request)
        resp = api_response(
            success=1,
            status_code=201,
            message="User signed up successfully",
            result={"user": result["user"]},  # tokens stay in cookies only
        )
        _set_auth_cookies(
            resp,
            result["access_token"],
            result["refresh_token"],
            result["csrf_token"],
        )
        return resp

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
@limiter.limit("10/minute")
async def login(
    login_request: LoginRequest,
    request: Request,
    db=Depends(get_db),
):
    try:
        result = await login_user(
            db, login_request.email, login_request.password, request
        )
        resp = api_response(
            success=1,
            status_code=200,
            message="User logged in successfully",
            result={"user": result["user"]},  # tokens stay in cookies only
        )
        _set_auth_cookies(
            resp,
            result["access_token"],
            result["refresh_token"],
            result["csrf_token"],
        )
        return resp

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(
    db=Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        result = await refresh_user_session(db, refresh_token)
        resp = api_response(
            success=1,
            status_code=200,
            message="Token refreshed successfully",
            result=None,
        )
        resp.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )
        resp.set_cookie(
            key="csrf_token",
            value=result["csrf_token"],
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return resp

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(
    db=Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
    _=Depends(verify_csrf_token),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        result = await logout_user(db, refresh_token)
        resp = api_response(
            success=1,
            status_code=200,
            message="User logged out successfully",
            result=result,
        )
        resp.delete_cookie(key="access_token", path="/")
        resp.delete_cookie(key="refresh_token", path=_REFRESH_COOKIE_PATH)
        resp.delete_cookie(key="csrf_token", path="/")
        return resp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot/password")
@limiter.limit("5/minute")
async def forgot_password_router(
    request: Request,
    body: ForgotPasswordRequest,
    db=Depends(get_db),
):
    try:
        result = await forgot_password_service(db, body.email)
        return api_response(
            success=1,
            status_code=200,
            message="Password reset link sent successfully",
            result=result,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset/password")
async def reset_password_router(request: ResetPasswordRequest, db=Depends(get_db)):
    try:
        user = await reset_password(db, request.token, request.new_password)
        return api_response(
            success=1,
            status_code=200,
            message="Password reset successfully",
            result=UserResponse.model_validate(user).model_dump(mode="json"),
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
