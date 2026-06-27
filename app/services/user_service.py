from app.models.user import User
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


async def create_user_service(db, user: UserCreate):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")
    
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise ValueError("Username already taken")
    
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    
    return await create_user(db, user)


async def update_user_service(db, user_id: str, user):
    existing_user = await get_user_by_id(db, user_id)
    if not existing_user:
        raise ValueError("User not found")
    
    if user.email and user.email != existing_user.email:
        if await get_user_by_email(db, user.email):
            raise ValueError("Email already registered")
        
    if user.username and user.username != existing_user.username:
        if await get_user_by_username(db, user.username):
            raise ValueError("Username already taken")
        
    return await update_user(db, user_id, user)



