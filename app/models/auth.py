from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
import datetime

from app.core.database import Base

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String, unique=True, index=True)
    refresh_token = Column(String, unique=True, index=True)
    csrf_token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")