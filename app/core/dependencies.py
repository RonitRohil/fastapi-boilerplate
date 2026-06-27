from app.core.database import SessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.repositories import user_repository


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = decode_access_token(token)  # raises ValueError if invalid/expired
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = user_repository.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_admin():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user or user.role != "admin":
                raise HTTPException(status_code=403, detail="Forbidden")
            return await func(*args, **kwargs)

        return wrapper

    return decorator



