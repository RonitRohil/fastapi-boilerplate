from fastapi import Depends, HTTPException, APIRouter, Request, Response
from app.services.auth_service import (
    forgot_password_service,
    login_user,
    refresh_user_session,
    logout_user,
    signup_user,
    reset_password,
)
from app.core.dependencies import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    SignupRequest,
    ResetPasswordRequest,
)
from app.core.response import api_response
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(
    sign_up_request: SignupRequest,
    request: Request,
    response: Response,
    db=Depends(get_db),
):
    try:
        result = await signup_user(db, sign_up_request, request)

        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,  # JS cannot read this
            secure=settings.COOKIE_SECURE,  # HTTPS only (set False locally for dev)
            samesite="lax",  # sent on same-site + top-level cross-site navs
            max_age=1800,  # 30 minutes (matches ACCESS_TOKEN_EXPIRE_MINUTES)
            path="/",
        )

        # refresh token — restrict path so it's only sent to the refresh endpoint
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=604800,  # 7 days
            path="/api/v1/auth/refresh",  # only sent when hitting refresh endpoint
        )

        # CSRF token — NOT httpOnly — JS must be able to read this
        response.set_cookie(
            key="csrf_token",
            value=result["csrf_token"],
            httponly=False,  # JS reads this and attaches to headers
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=1800,
        )

        return api_response(
            success=1,
            status_code=200,
            message="User signed up successfully",
            result=result,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(
    login_request: LoginRequest,
    request: Request,
    response: Response,
    db=Depends(get_db),
):
    try:
        result = await login_user(
            db, login_request.email, login_request.password, request
        )

        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,  # JS cannot read this
            secure=settings.COOKIE_SECURE,  # HTTPS only (set False locally for dev)
            samesite="lax",  # sent on same-site + top-level cross-site navs
            max_age=1800,  # 30 minutes (matches ACCESS_TOKEN_EXPIRE_MINUTES)
            path="/",
        )

        # refresh token — restrict path so it's only sent to the refresh endpoint
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=604800,  # 7 days
            path="/api/v1/auth/refresh",  # only sent when hitting refresh endpoint
        )

        # CSRF token — NOT httpOnly — JS must be able to read this
        response.set_cookie(
            key="csrf_token",
            value=result["csrf_token"],
            httponly=False,  # JS reads this and attaches to headers
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=1800,
        )

        return api_response(
            success=1,
            status_code=200,
            message="User logged in successfully",
            result=result,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(request: RefreshTokenRequest, response: Response, db=Depends(get_db)):
    try:
        result = await refresh_user_session(db, request.refresh_token)
        response.set_cookie(
            key="access_token",
            value=result["access_token"],
            httponly=True,  # JS cannot read this
            secure=settings.COOKIE_SECURE,  # HTTPS only (set False locally for dev)
            samesite="lax",  # sent on same-site + top-level cross-site navs
            max_age=1800,  # 30 minutes (matches ACCESS_TOKEN_EXPIRE_MINUTES)
            path="/",
        )

        # CSRF token — NOT httpOnly — JS must be able to read this
        response.set_cookie(
            key="csrf_token",
            value=result["csrf_token"],
            httponly=False,  # JS reads this and attaches to headers
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=1800,
        )

        return api_response(
            success=1,
            status_code=200,
            message="User token refreshed successfully",
            result=result,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(request: LogoutRequest, response: Response, db=Depends(get_db)):
    try:
        user = await logout_user(db, request.refresh_token)

        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")
        response.delete_cookie(key="csrf_token", path="/")

        return api_response(
            success=1,
            status_code=200,
            message="User logged out successfully",
            result=user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/forgot/password")
async def forgot_password_router(request: ForgotPasswordRequest, db=Depends(get_db)):
    try:
        forgot_password_result = await forgot_password_service(db, request.email)

        return api_response(
            success=1,
            status_code=200,
            message="Password reset link sent successfully",
            result=forgot_password_result,
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
            result=user,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
