from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone
from typing import Optional

from app.database import get_db
from app.models.profile import Profile
from app.config import settings

router = APIRouter()

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@router.get("/daily-batch")
async def get_n8n_daily_batch(
    limit: int = Query(50, le=200),
    min_score: int = Query(60),
    no_website: bool = Query(True),
    mark_as_sent: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    stmt = select(Profile).where(Profile.contacted_at.is_(None))
    
    if min_score is not None:
        stmt = stmt.where(Profile.lead_score >= min_score)
    if no_website:
        stmt = stmt.where(Profile.has_website == False)
        
    stmt = stmt.order_by(desc(Profile.lead_score)).limit(limit)
    
    result = await db.execute(stmt)
    profiles = result.scalars().all()
    
    response_data = []
    
    for p in profiles:
        response_data.append({
            "id": p.id,
            "instagram_url": p.ig_profile_url or f"https://instagram.com/{p.username}",
            "full_name": p.full_name,
            "email": p.business_email,
            "email_confidence": 95, # Mock, normally from emails table join
            "phone": p.business_phone,
            "category": p.detected_category,
            "biography": p.biography,
            "follower_count": p.follower_count,
            "has_website": p.has_website,
            "website_url": p.external_url,
            "lead_score": p.lead_score,
            "last_5_posts": [], # Mock, normally from posts table join
            "personalization_context": p.personalization_context
        })
        
        if mark_as_sent:
            p.contacted_at = datetime.now(timezone.utc)
            
    if mark_as_sent and profiles:
        await db.commit()
        
    return response_data
