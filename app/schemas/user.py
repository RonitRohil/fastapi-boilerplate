from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = True
    role: str | None = "user"


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    role: str | None = None


class UserSelfUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    is_verified: bool
    role: str
    created_at: str
    updated_at: str
    created_by: str | None = None
    updated_by: str | None = None


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
