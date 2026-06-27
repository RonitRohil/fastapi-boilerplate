from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String, unique=True, index=True)
    device_name = Column(String(200), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")


class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(
        String(36), ForeignKey("user_sessions.session_id"), nullable=False, index=True
    )
    token_type = Column(String(20), nullable=False, default="refresh")
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tokens")
