import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.proxy import Proxy
from app.exceptions import ProxyException

class ProxyManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_proxy(self) -> Proxy:
        stmt = select(Proxy).where(Proxy.is_active == True).order_by(Proxy.last_used.asc().nulls_first())
        result = await self.db.execute(stmt)
        proxies = result.scalars().all()
        
        if not proxies:
            raise ProxyException("No active proxies available")
            
        # Select from the top 3 least recently used to add randomness
        top_candidates = proxies[:3]
        selected_proxy = random.choice(top_candidates)
        
        selected_proxy.last_used = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(selected_proxy)
        
        return selected_proxy

    async def mark_success(self, proxy_id: int):
        proxy = await self.db.get(Proxy, proxy_id)
        if proxy:
            proxy.success_count += 1
            await self.db.commit()

    async def mark_failure(self, proxy_id: int):
        proxy = await self.db.get(Proxy, proxy_id)
        if proxy:
            proxy.fail_count += 1
            if proxy.fail_count >= 3:
                proxy.is_active = False
            await self.db.commit()
