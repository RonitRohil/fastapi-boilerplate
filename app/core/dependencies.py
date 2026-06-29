from app.core.database import SessionLocal
from fastapi import Depends, HTTPException, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import user_repository


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


http_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    access_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    bearer_credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    db=Depends(get_db),
):
    # Priority: cookie (web) > bearer from Swagger UI > raw Authorization header
    token = None
    if access_token:
        token = access_token
    elif bearer_credentials:
        token = bearer_credentials.credentials  # already stripped of "Bearer " prefix
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user_id = payload.get("sub")
    user = user_repository.get_user_by_id(db, user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def verify_csrf_token(
    x_csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
    access_token: str | None = Cookie(default=None),
):
    if not x_csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token missing")

    try:
        csrf_payload = decode_access_token(x_csrf_token)
        access_payload = decode_access_token(access_token) if access_token else None

    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # Both must belong to the same session
    if access_payload and csrf_payload.get("session_id") != access_payload.get(
        "session_id"
    ):
        raise HTTPException(status_code=403, detail="CSRF token does not match session")

    return True
