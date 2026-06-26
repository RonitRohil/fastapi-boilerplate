from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserSelfUpdate, UserResponse, UserListResponse


def get_user_by_id(db, user_id: str):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


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
