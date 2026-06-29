import uuid as _uuid
from datetime import datetime, timezone

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_id(db, user_id: str):
    return db.query(User).filter(User.id == _uuid.UUID(str(user_id))).first()


def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db, user: UserCreate, hashed_password: str, current_user) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,  # user created by admin can be admin also.
        is_active=True,
        created_by=current_user.id,
        updated_by=current_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_user_no_commit(db, user, hashed_password: str) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role="user",  # hardcoded — public signup cannot self-assign role
        is_active=True,
    )

    db.add(db_user)
    return db_user


def update_user(db, user_id: str, user, current_user):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        for key, value in user.model_dump(exclude_unset=True).items():
            if key == "password":
                db_user.hashed_password = hash_password(value)  # hash + correct column
            else:
                setattr(db_user, key, value)
        db_user.updated_by = current_user.id
        db_user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_user)

    return db_user


def inactivate_user(db, user_id: str, current_user):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = False
        db_user.updated_by = current_user.id
        db_user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_user)
    return db_user


def activate_user(db, user_id: str, current_user):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = True
        db_user.updated_by = current_user.id
        db_user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db, user_id: str, current_user):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.updated_by = current_user.id
        db_user.updated_at = datetime.now(timezone.utc)
        db.delete(db_user)

        db.commit()
        return db_user
    return None


def get_users(
    db,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    role: str | None = None,
):
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    if role is not None:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()


def get_users_count(
    db,
    is_active: bool | None = None,
    is_verified: bool | None = None,
    role: str | None = None,
):
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    if role is not None:
        query = query.filter(User.role == role)
    return query.count()
