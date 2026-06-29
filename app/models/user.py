from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    UUID,
    Enum,
    ForeignKey,
)
from datetime import datetime, timezone
from app.core.database import Base
import uuid
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum("user", "admin", name="user_roles"), default="user")
    is_verified = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    sessions = relationship(
        "UserSession", back_populates="user", foreign_keys="UserSession.user_id"
    )

    tokens = relationship(
        "UserToken", back_populates="user", foreign_keys="UserToken.user_id"
    )
