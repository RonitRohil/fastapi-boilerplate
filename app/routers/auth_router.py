from fastapi import Depends, HTTPException, APIRouter, Request
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

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(sign_up_request: SignupRequest, request: Request, db=Depends(get_db)):
    try:
        user = await signup_user(db, sign_up_request, request)

        return api_response(
            success=1,
            status_code=200,
            message="User signed up successfully",
            result=user,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(login_request: LoginRequest, request: Request, db=Depends(get_db)):
    try:
        user = await login_user(
            db, login_request.email, login_request.password, request
        )
        return api_response(
            success=1,
            status_code=200,
            message="User logged in successfully",
            result=user,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(request: RefreshTokenRequest, db=Depends(get_db)):
    try:
        user = await refresh_user_session(db, request.refresh_token)
        return api_response(
            success=1,
            status_code=200,
            message="User token refreshed successfully",
            result=user,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(request: LogoutRequest, db=Depends(get_db)):
    try:
        user = await logout_user(db, request.refresh_token)
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
