from datetime import datetime, timedelta, timezone
import uuid

from app.core.config import settings
from app.schemas.user import UserCreate, UserResponse
from app.core.security import (
    create_password_reset_token,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    create_csrf_token,
)
from app.repositories.user_repository import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    create_user_no_commit,
)
from app.repositories.auth_repository import (
    add_user_token_no_commit,
    create_user_session_no_commit,
    get_user_session,
    get_user_token_with_jti,
    revoke_all_user_sessions_no_commit,
    revoke_all_user_tokens_no_commit,
    revoke_user_session_no_commit,
    revoke_user_token_no_commit,
)
from app.schemas.auth import AddUserToken, UserSessionCreate


def _refresh_token_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


async def signup_user(db, user: UserCreate, request):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")

    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already taken")

    try:
        hashed_password = hash_password(user.password)
        db_user = create_user_no_commit(db, user, hashed_password)
        db.flush()

        session_id = str(uuid.uuid4())
        user_dict = {
            "id": str(db_user.id),
            "username": db_user.username,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "is_verified": db_user.is_verified,
            "session_id": session_id,
        }

        access_token = create_access_token(user_dict)
        refresh_token = create_refresh_token(user_dict)
        csrf_token = create_csrf_token(user_dict)

        refresh_payload = decode_access_token(refresh_token)
        jti = refresh_payload.get("jti")
        expires_at = _refresh_token_expires_at()

        create_user_session_no_commit(
            db,
            UserSessionCreate(
                user_id=str(db_user.id),
                session_id=session_id,
                expires_at=expires_at,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None,
                device_name=request.headers.get("Device-Name"),
            ),
        )

        add_user_token_no_commit(
            db,
            AddUserToken(
                jti=jti,
                user_id=str(db_user.id),
                session_id=session_id,
                token_type="refresh",
                expires_at=expires_at,
            ),
        )

        db.commit()
        db.refresh(db_user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "csrf_token": csrf_token,
            "user": UserResponse.model_validate(db_user).model_dump(mode="json"),
        }

    except Exception as e:
        db.rollback()
        raise e


async def login_user(db, email: str, password: str, request):
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")

    try:
        session_id = str(uuid.uuid4())
        user_dict = {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "role": user.role,
            "session_id": session_id,
        }

        access_token = create_access_token(user_dict)
        refresh_token = create_refresh_token(user_dict)
        csrf_token = create_csrf_token(user_dict)

        refresh_payload = decode_access_token(refresh_token)
        jti = refresh_payload.get("jti")
        expires_at = _refresh_token_expires_at()

        create_user_session_no_commit(
            db,
            UserSessionCreate(
                user_id=str(user.id),
                session_id=session_id,
                expires_at=expires_at,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host if request.client else None,
                device_name=request.headers.get("Device-Name"),
            ),
        )

        add_user_token_no_commit(
            db,
            AddUserToken(
                jti=jti,
                user_id=str(user.id),
                session_id=session_id,
                token_type="refresh",
                expires_at=expires_at,
            ),
        )

        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "csrf_token": csrf_token,
            "user": UserResponse.model_validate(user).model_dump(mode="json"),
        }

    except Exception as e:
        db.rollback()
        raise e


async def refresh_user_session(db, refresh_token: str):
    try:
        payload = decode_access_token(refresh_token)
    except ValueError:
        raise ValueError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    session_id = payload.get("session_id")
    user_id = payload.get("sub")

    session = get_user_session(db, session_id)
    if not session:
        raise ValueError("Invalid session")

    if session.revoked_at:
        raise ValueError("Session has been revoked")

    # Reject sessions whose expiry has passed even without explicit revocation
    if session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Session has expired")

    jti = payload.get("jti")
    token_record = get_user_token_with_jti(db, jti)
    if not token_record:
        raise ValueError("Refresh token not found")

    if token_record.revoked_at is not None:
        raise ValueError("Refresh token has been revoked")

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    user_dict = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "role": user.role,
        "session_id": session_id,
    }

    new_access_token = create_access_token(user_dict)
    new_csrf_token = create_csrf_token(user_dict)

    return {"access_token": new_access_token, "csrf_token": new_csrf_token}


async def logout_user(db, refresh_token: str):
    try:
        payload = decode_access_token(refresh_token)
    except ValueError:
        raise ValueError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Not a refresh token")

    session_id = payload.get("session_id")
    jti = payload.get("jti")

    revoke_user_session_no_commit(db, session_id)
    revoke_user_token_no_commit(db, jti)

    db.commit()

    return {"message": "User logged out successfully"}


async def forgot_password_service(db, email: str):
    user = get_user_by_email(db, email)

    if user:
        reset_token, jti = create_password_reset_token(user.id)
        add_user_token_no_commit(
            db,
            AddUserToken(
                jti=jti,
                user_id=str(user.id),
                session_id=None,
                token_type="password_reset",
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
            ),
        )
        db.commit()

        if settings.DEBUG:
            return {
                "message": "If that email is registered, a reset link has been sent",
                "debug_token": reset_token,
            }

    return {"message": "If that email is registered, a reset link has been sent"}


async def reset_password(db, token: str, new_password: str):
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise ValueError("Reset link is invalid or expired")

    if payload.get("purpose") != "password_reset":
        raise ValueError("Invalid token")

    jti = payload.get("jti")
    if not jti:
        raise ValueError("Invalid token format")

    token_record = get_user_token_with_jti(db, jti)
    if not token_record:
        raise ValueError("Reset token not found or already used")
    if token_record.revoked_at is not None:
        raise ValueError("Reset token has already been used")

    user_id = payload.get("sub")
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    user.hashed_password = hash_password(new_password)

    # Mark the reset token as used (one-time use enforcement)
    revoke_user_token_no_commit(db, jti)

    # Revoke all sessions so attacker cannot stay logged in after a reset
    revoke_all_user_sessions_no_commit(db, user_id)
    revoke_all_user_tokens_no_commit(db, user_id)

    db.commit()
    db.refresh(user)
    return user
