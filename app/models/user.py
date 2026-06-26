from sqlalchemy import Column, DateTime, Integer, String, Boolean, UUID, ENUM, ForeignKey
from datetime import datetime

from sqlalchemy.orm import relationship


class Users():
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, ENUM("user", "admin", name="user_roles"), default="user")
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID, ForeignKey("users.id"), nullable=True)

