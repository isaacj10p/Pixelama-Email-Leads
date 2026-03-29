from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    biography = Column(Text)
    external_url = Column(String)
    
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    
    is_business_account = Column(Boolean, default=False)
    business_category_name = Column(String)
    business_email = Column(String)
    business_phone = Column(String)
    
    detected_category = Column(String)
    lead_score = Column(Integer, default=0)
    has_website = Column(Boolean, default=False)
    personalization_context = Column(Text)
    
    ig_profile_url = Column(String)
    profile_pic_url = Column(String)
    
    contacted_at = Column(DateTime(timezone=True))
    contact_notes = Column(Text)
    
    last_scraped = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    posts = relationship("Post", back_populates="profile", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="profile", cascade="all, delete-orphan")
