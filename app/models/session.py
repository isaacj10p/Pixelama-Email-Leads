from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base

class IGSession(Base):
    __tablename__ = "ig_sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    cookies_json = Column(Text)
    last_used = Column(DateTime(timezone=True))
    is_healthy = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
