from app.models.user import User
from app.schemas import user
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.repositories.user_repository import (
    get_user_by_id,
    get_user_by_email,
    create_user,
)


def signup_user(db, user: UserCreate):
    # Validate email uniqueness
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Validate username uniqueness
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise ValueError("Username already taken")

    password = user.password
    # Hash the password before storing it in the database
    hashed_password = hash_password(password)
    user.password = hashed_password

    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")

    # Verify the password
    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password")
    
    # Create an access token for the user
    access_token = create_access_token(user.id)
    user.access_token = access_token
    
    # Create a user session in the database
    from app.repositories.auth_repository import create_user_session
    from app.schemas.auth import UserSessionCreate
    user_session_data = UserSessionCreate(user_id=user.id, session_id=access_token)
    create_user_session(db, user_session_data)

    return user


def verify_password(plain_password, hashed_password):
    import bcrypt

    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def refresh_user_session(db, user_id: str):
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

