from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    shortcode = Column(String, unique=True, index=True, nullable=False)
    caption = Column(Text)
    
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True))
    post_url = Column(String)

    profile = relationship("Profile", back_populates="posts")
