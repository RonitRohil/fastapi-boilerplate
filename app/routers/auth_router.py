from fastapi import Depends, HTTPException, APIRouter
from app.services.auth_service import (
    login_user,
    refresh_user_session,
    logout_user,
    signup_user,
)
from app.core.dependencies import get_db
from app.schemas.auth import SignupRequest
from app.core.reponse import api_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(email: str, password: str, db=Depends(get_db)):
    try:
        user = await login_user(db, email, password)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(user_id: str, db=Depends(get_db)):
    try:
        user = await refresh_user_session(db, user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(user_id: str, db=Depends(get_db)):
    try:
        user = await logout_user(db, user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signup")
async def signup(user: SignupRequest, db=Depends(get_db)):
    try:
        user = await signup_user(db, user)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset/password")
async def reset_password(user_id: str, new_password: str, db=Depends(get_db)):
    try:
        user = await reset_password(db, user_id, new_password)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))