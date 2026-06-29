from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = True
    role: str | None = "user"


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    role: str | None = None


class UserSelfUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID  # UUID(as_uuid=True) in ORM → must be UUID, not str
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None  # FK to users.id — UUID(as_uuid=True)
    updated_by: UUID | None = None


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
