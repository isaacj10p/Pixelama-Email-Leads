from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.profile import Profile
from app.models.post import Post
from app.models.email import Email

router = APIRouter()

@router.get("/")
async def get_leads(
    limit: int = 50,
    offset: int = 0,
    min_score: Optional[int] = None,
    has_email: Optional[bool] = None,
    category: Optional[str] = None,
    no_website: Optional[bool] = None,
    order_by: str = "score", # score | created_at | follower_count
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile)
    
    if min_score is not None:
        stmt = stmt.where(Profile.lead_score >= min_score)
    if has_email is True:
        stmt = stmt.where(Profile.business_email.isnot(None))
    if category:
        stmt = stmt.where(Profile.detected_category == category)
    if no_website is True:
        stmt = stmt.where(Profile.has_website == False)
        
    if order_by == "score":
        stmt = stmt.order_by(desc(Profile.lead_score))
    elif order_by == "created_at":
        stmt = stmt.order_by(desc(Profile.created_at))
    elif order_by == "follower_count":
        stmt = stmt.order_by(desc(Profile.follower_count))
        
    stmt = stmt.offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    profiles = result.scalars().all()
    
    return profiles

@router.get("/{profile_id}")
async def get_lead(profile_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Profile).where(Profile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    return profile

@router.post("/{profile_id}/log-contact")
async def log_contact(profile_id: int, note: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    profile = await db.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    profile.contacted_at = datetime.now(timezone.utc)
    if note:
        profile.contact_notes = note
        
    await db.commit()
    return {"ok": True}

@router.get("/export")
async def export_leads(
    format: str = "json",
    limit: int = Query(1000, le=10000),
    db: AsyncSession = Depends(get_db)
):
    # Simplistic export, depending on format we would return StreamingResponse
    return {"msg": f"Export in {format} format not fully implemented yet."}
