from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class DomainPattern(Base):
    __tablename__ = "domain_patterns"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    dominant_pattern = Column(String)
    sample_size = Column(Integer, default=0)
    confirmed_at = Column(DateTime(timezone=True), server_default=func.now())

class MXCache(Base):
    __tablename__ = "mx_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    mx_host = Column(String)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
