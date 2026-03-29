import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.seed import SeedAccount
from app.models.proxy import Proxy

async def populate_db():
    print("Populating initial data...")
    async with AsyncSessionLocal() as db:
        
        # Insert Initial Seeds
        seeds = [
            SeedAccount(username="example_dentist", niche="dental"),
            SeedAccount(username="example_lawyer", niche="abogado"),
            SeedAccount(username="example_clinic", niche="medico")
        ]
        
        db.add_all(seeds)
        
        # Insert Initial Proxies
        proxies = [
            Proxy(proxy_url="socks5://user:pass@127.0.0.1:9050"),
            Proxy(proxy_url="socks5://user:pass@127.0.0.2:9050")
        ]
        
        db.add_all(proxies)
        
        await db.commit()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(populate_db())
