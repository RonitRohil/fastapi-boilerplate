from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserSelfUpdate,
    UserResponse,
    UserListResponse,
)


async def get_user_by_id(db, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


async def get_user_by_username(db, username: str):
    return db.query(User).filter(User.username == username).first()


async def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()


async def create_user(db, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


async def update_user(db, user_id: str, user: UserUpdate):
    db_user = await get_user_by_id(db, user_id)
    if db_user:
        for key, value in user.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


async def inactivate_user(db, user_id: str):
    db_user = await get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = False
        db.commit()
        db.refresh(db_user)
    return db_user


async def activate_user(db, user_id: str):
    db_user = await get_user_by_id(db, user_id)
    if db_user:
        db_user.is_active = True
        db.commit()
        db.refresh(db_user)
    return db_user


async def delete_user(db, user_id: str):
    db_user = await get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None


async def get_users(
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


async def get_users_count(db):
    return db.query(User).count()
