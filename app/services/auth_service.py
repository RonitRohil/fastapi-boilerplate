from datetime import datetime, timedelta, timezone
import uuid

from app.models.user import User
from app.schemas.user import UserCreate
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
    revoke_all_user_sessions,
    revoke_all_user_sessions_no_commit,
    revoke_all_user_tokens_no_commit,
    revoke_user_session,
    revoke_user_session_no_commit,
    revoke_user_token_no_commit,
)
from app.schemas.auth import UserSessionCreate


async def signup_user(db, user: UserCreate, request):
    # Validate email uniqueness
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")

    # Validate username uniqueness
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already taken")

    try:
        hashed_password = hash_password(user.password)
        user.password = hashed_password

        db_user = create_user_no_commit(db, user)
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

        db_session = create_user_session_no_commit(
            db,
            {
                "user_id": db_user.id,
                "session_id": session_id,
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
                "user_agent": request.headers.get("User-Agent"),
                "ip_address": request.client.host,
                "device_name": request.headers.get("Device-Name"),
            },
        )

        db_token = add_user_token_no_commit(
            db,
            {
                "user_id": db_user.id,
                "session_id": session_id,
                "jti": jti,
                "token_type": "refresh",
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            },
        )

        db.commit()
        db.refresh(db_user)
        db.refresh(db_session)
        db.refresh(db_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "csrf_token": csrf_token,
            "user_details": db_user,
        }

    except Exception as e:
        db.rollback()
        raise e


async def login_user(db, email: str, password: str, request):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")

    password_verification = await verify_password(password, user.hashed_password)
    if not password_verification:
        raise ValueError("Invalid email or password")

    try:
        session_id = str(uuid.uuid4())

        user_dict = {
            "id": user.id,
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

        db_session = create_user_session_no_commit(
            db,
            {
                "user_id": user.id,
                "session_id": session_id,
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
                "user_agent": request.headers.get("User-Agent"),
                "ip_address": request.client.host,
                "device_name": request.headers.get("Device-Name"),
            },
        )

        db_token = add_user_token_no_commit(
            db,
            {
                "user_id": user.id,
                "session_id": session_id,
                "jti": jti,
                "token_type": "refresh",
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            },
        )

        db.commit()
        db.refresh(db_session)
        db.refresh(db_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "csrf_token": csrf_token,
            "user_details": user,
        }

    except Exception as e:
        db.rollback()
        raise e


async def refresh_user_session(db, refresh_token: str):
    try:
        payload = decode_access_token(refresh_token)
    except ValueError as e:
        raise ValueError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    session_id = payload.get("session_id")
    user_id = payload.get("user_id")

    session = get_user_session(db, session_id)

    if not session:
        raise ValueError("Invalid session")

    if session.revoked_at:
        raise ValueError("Session has been revoked")

    jti = payload.get("jti")

    token_record = get_user_token_with_jti(db, jti)

    if not token_record and token_record.revoked_at is not None:
        raise ValueError("Refresh token has been revoked")

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "role": user.role,
    }

    new_access_token = create_access_token(user_dict)
    new_csrf_token = create_csrf_token(user_dict)

    return {"access_token": new_access_token, "csrf_token": new_csrf_token}


async def logout_user(db, user_id: str):
    # Logic to logout the user
    user = get_user_by_id(db, user_id)

    if not user:
        raise ValueError("User not found")

    revoke_session = await revoke_user_session_no_commit(db, user_id)

    revoke_token = await revoke_user_token_no_commit(db, user_id)

    db.commit()
    db.refresh(revoke_session)
    db.refresh(revoke_token)

    return {"message": "User logged out successfully"}


async def forgot_password_service(db, email: str):
    user = get_user_by_email(db, email)

    if not user:
        raise ValueError("User with email not found.")

    reset_token = create_password_reset_token(user.id)

    # For production send email

    return reset_token


async def reset_password(db, token: str, new_password: str):
    # Logic to reset the user password
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise ValueError("Resent link is invalid or expired")

    if payload.get("purpose") != "password_reset":
        raise ValueError("Invalid token")

    user_id = payload.get("sub")
    user = get_user_by_id(db, user_id)

    if not user:
        raise ValueError("User not found")

    hashed_password = hash_password(new_password)
    user.hashed_password = hashed_password

    # Revoke all sessions
    user_sessions = await revoke_all_user_sessions_no_commit(db, user_id)

    user_tokens = await revoke_all_user_tokens_no_commit(db, user_id)

    db.commit()
    db.refresh(user)
    db.refresh(user_sessions)
    db.refresh(user_tokens)

    return user
