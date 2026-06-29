from app.schemas.user import UserCreate
from app.core.security import hash_password
from app.repositories.user_repository import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user,
    inactivate_user,
    activate_user,
    delete_user,
    get_users,
    get_users_count,
)


async def create_user_service(db, user: UserCreate, current_user):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")

    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already taken")

    hashed_password = hash_password(user.password)
    return create_user(db, user, hashed_password, current_user)


async def update_user_service(db, user_id: str, user, current_user):
    existing_user = get_user_by_id(db, user_id)
    if not existing_user:
        raise ValueError("User not found")

    if hasattr(user, "email") and user.email and user.email != existing_user.email:
        if get_user_by_email(db, user.email):
            raise ValueError("Email already registered")

    if (
        hasattr(user, "username")
        and user.username
        and user.username != existing_user.username
    ):
        if get_user_by_username(db, user.username):
            raise ValueError("Username already taken")

    return update_user(db, user_id, user, current_user)


async def get_user_service(db, user_id: str):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    return user


async def get_users_list_service(db, page: int, page_size: int, filters):
    skip = (page - 1) * page_size
    limit = page_size

    is_active = filters.get("is_active")
    is_verified = filters.get("is_verified")
    role = filters.get("role")

    users = get_users(db, skip, limit, is_active, is_verified, role)
    total = get_users_count(db, is_active=is_active, is_verified=is_verified, role=role)

    return {"users": users, "total": total, "page": page, "page_size": page_size}


async def update_user_status_service(db, user_id: str, current_user):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    if user.is_active:
        return inactivate_user(db, user_id, current_user)
    else:
        return activate_user(db, user_id, current_user)


async def delete_user_service(db, user_id: str, current_user):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    return delete_user(db, user_id, current_user)
