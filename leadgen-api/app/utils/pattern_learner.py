from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.domain import DomainPattern

class PatternLearner:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def update_pattern(self, domain: str, pattern: str):
        stmt = select(DomainPattern).where(DomainPattern.domain == domain)
        res = await self.db.execute(stmt)
        record = res.scalars().first()
        
        if record:
            # Simplistic learning: update to latest successful pattern
            # Robust would be keeping counts map
            record.dominant_pattern = pattern
            record.sample_size += 1
        else:
            new_record = DomainPattern(domain=domain, dominant_pattern=pattern, sample_size=1)
            self.db.add(new_record)
            
        await self.db.commit()
