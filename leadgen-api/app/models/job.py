from sqlalchemy import Column, Integer, String, DateTime, Float, func
from app.database import Base

class JobRun(Base):
    __tablename__ = "job_runs"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    profiles_scraped = Column(Integer, default=0)
    emails_found = Column(Integer, default=0)
    emails_valid = Column(Integer, default=0)
    
    avg_score = Column(Float, default=0.0)
    stop_reason = Column(String)
