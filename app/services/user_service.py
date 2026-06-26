from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.repositories.user_repository import (
    get_user_by_id,
    get_user_by_email,
    create_user,
    update_user,
    inactivate_user,
    activate_user,
    delete_user,
    get_users,
    get_users_count,
)


def create_user(db, user: UserCreate):
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


def update_user(db, user_id: str, user: UserCreate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def get_user_by_id(db, user_id: str):
    return get_user_by_id(db, user_id)


def get_user_by_email(db, email: str):
    return get_user_by_email(db, email)


def get_users(db, skip: int = 0, limit: int = 100):
    users = get_users(db, skip=skip, limit=limit)
    user_count = get_users_count(db)
    return users, user_count


def inactivate_user(db, user_id: str):
    return inactivate_user(db, user_id)


def activate_user(db, user_id: str):
    return activate_user(db, user_id)


def delete_user(db, user_id: str):
    return delete_user(db, user_id)
