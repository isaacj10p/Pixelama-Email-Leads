from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base

class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True, index=True)
    proxy_url = Column(String, unique=True, nullable=False)
    
    last_used = Column(DateTime(timezone=True))
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
