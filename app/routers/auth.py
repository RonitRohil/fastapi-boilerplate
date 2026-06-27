from fastapi import Depends, HTTPException, APIRouter
from app.services.auth_service import login_user, refresh_user_session

router = APIRouter()



def login(db, email: str, password: str):
    return login_user(db, email, password)


def refresh_session(db, user_id: str):
    return refresh_user_session(db, user_id)
