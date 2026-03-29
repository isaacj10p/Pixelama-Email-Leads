from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from app.database import Base

class SeedAccount(Base):
    __tablename__ = "seed_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    niche = Column(String)
    
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True))
    total_followers_scraped = Column(Integer, default=0)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
