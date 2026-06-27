from fastapi import Depends, HTTPException, APIRouter
from app.services.auth_service import (
    login_user,
    refresh_user_session,
    logout_user,
    signup_user,
    reset_password,
)
from app.core.dependencies import get_db
from app.schemas.auth import LoginRequest, SignupRequest, ResetPasswordRequest
from app.core.response import api_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(login_request=LoginRequest, db=Depends(get_db)):
    try:
        user = await login_user(db, login_request.email, login_request.password)
        return api_response(
            success=1,
            status_code=200,
            message="User logged in successfully",
            result=user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(user_id: str, db=Depends(get_db)):
    try:
        user = await refresh_user_session(db, user_id)
        return api_response(
            success=1,
            status_code=200,
            message="User session refreshed successfully",
            result=user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(user_id: str, db=Depends(get_db)):
    try:
        user = await logout_user(db, user_id)
        return api_response(
            success=1,
            status_code=200,
            message="User logged out successfully",
            result=user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signup")
async def signup(user: SignupRequest, db=Depends(get_db)):
    try:
        user = await signup_user(db, user)
        return api_response(
            success=1,
            status_code=200,
            message="User signed up successfully",
            result=user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset/password")
async def reset_password_router(request=ResetPasswordRequest, db=Depends(get_db)):
    try:
        user = await reset_password(db, request)
        return api_response(
            success=1,
            status_code=200,
            message="Password reset successfully",
            result=user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
