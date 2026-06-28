from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserSelfUpdate,
    UserResponse,
    UserListResponse,
)


def get_user_by_id(db, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,  # user created by admin can be admin also.
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_user_no_commit(db, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,  # user created by admin can be admin also.
        is_active=True,
    )

    db.add(db_user)
    return db_user


def update_user(db, user_id: str, user: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        for key, value in user.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def inactivate_user(db, user_id: str):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
    return db_user


def activate_user(db, user_id: str):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db, user_id: str):
    db_user = get_user_by_id(db, user_id)
    if db_user:
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


def get_users_count(db):
    return db.query(User).count()
