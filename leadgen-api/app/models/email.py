from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False, index=True)
    
    source = Column(String) # bio | smtp | inferred | api
    verification_status = Column(String) # valid | invalid | catch-all | unverifiable
    confidence_score = Column(Integer, default=0)
    
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="emails")
