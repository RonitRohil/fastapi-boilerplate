from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
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
    create_user,
)
from app.repositories.auth_repository import create_user_session, revoke_user_session
from app.schemas.auth import UserSessionCreate


async def signup_user(db, user: UserCreate):
    # Validate email uniqueness
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")

    # Validate username uniqueness
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already taken")

    password = user.password
    # Hash the password before storing it in the database
    hashed_password = hash_password(password)
    user.password = hashed_password

    db_user = await create_user(db, user)

    if db_user is None:
        raise ValueError("User creation failed")

    # Initiate Login Process
    token_data = await login_process(db, db_user)

    if token_data is None:
        raise ValueError("Login process failed")

    return token_data


async def login_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")

    # Verify the password
    verify_pass = verify_password(password, user.hashed_password)
    if verify_pass == False:
        raise ValueError("Invalid email or password")

    token_data = await login_process(db, user)

    if token_data is None:
        raise ValueError("Login process failed")

    return token_data


async def refresh_user_session(db, user_id: str):
    # Logic to refresh the user session
    user = get_user_by_id(db, user_id)

    if not user:
        raise ValueError("User not found")

    decode_token = decode_access_token(user.access_token)

    if decode_token and decode_token.get("sub") == user_id:
        # Token is still valid, no need to refresh
        return user.access_token

    # Token is expired or invalid, generate a new one
    new_access_token = create_access_token(user_id)
    user.access_token = new_access_token
    db.commit()
    db.refresh(user)
    return new_access_token


async def login_process(db, user):
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

    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user_dict)

    session_data = UserSessionCreate(
        user_id=user.id,
        session_id=access_token,
        refresh_token=refresh_token,
        csrf_token=csrf_token,
    )

    session = await create_user_session(db, session_data)

    user_dict["session_id"] = session.session_id

    csrf_token = create_csrf_token(user_dict)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "csrf_token": csrf_token,
    }


async def logout_user(db, user_id: str):
    # Logic to logout the user
    user = get_user_by_id(db, user_id)

    if not user:
        raise ValueError("User not found")

    revoke_session = await revoke_user_session(db, user_id)
    return revoke_session


async def reset_password(db, request):
    # Logic to reset the user password
    user = get_user_by_email(db, request.email)

    if not user:
        raise ValueError("User not found")

    hashed_password = hash_password(request.new_password)
    user.hashed_password = hashed_password

    db.commit()
    db.refresh(user)

    return user
