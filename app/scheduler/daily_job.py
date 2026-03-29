import asyncio
from typing import Optional
from loguru import logger
from datetime import datetime, timezone, timedelta
from app.scheduler.celery_app import app
from app.database import AsyncSessionLocal
from sqlalchemy import select

from app.models.seed import SeedAccount
from app.models.job import JobRun
from app.scraper.instagram import InstagramScraper
from app.config import settings

async def _run_async_job():
    async with AsyncSessionLocal() as db:
        job = JobRun(started_at=datetime.now(timezone.utc))
        db.add(job)
        await db.commit()
        
        start_time = datetime.now()
        max_duration = timedelta(minutes=settings.JOB_MAX_MINUTES)
        
        scraper = InstagramScraper(db)
        
        try:
            # Load active seeds
            stmt = select(SeedAccount).where(SeedAccount.is_active == True).order_by(SeedAccount.last_scraped.asc().nullsfirst())
            res = await db.execute(stmt)
            seeds = res.scalars().all()
            
            if not seeds:
                logger.warning("No active seed accounts found.")
                job.stop_reason = "No seeds"
                
            else:
                for seed in seeds:
                    elapsed = datetime.now() - start_time
                    if elapsed >= max_duration:
                        job.stop_reason = "Time Limit Reached"
                        break
                        
                    if job.emails_valid >= settings.JOB_TARGET_LEADS:
                        job.stop_reason = "Target Leads Reached"
                        break
                        
                    try:
                        await scraper.run_extraction_for_seed(seed)
                        
                        # In reality we'd track specific counts here, mocked for now
                        job.profiles_scraped += 50
                        job.emails_found += 20
                        job.emails_valid += 15
                        
                    except Exception as e:
                        logger.error(f"Error scraping seed {seed.username}: {e}")
                
                if not job.stop_reason:
                    job.stop_reason = "Finished Seeds"
                    
        except Exception as e:
            logger.exception("Job execution failed")
            job.stop_reason = f"Error: {e}"
            
        finally:
            job.ended_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"Job completed: {job.stop_reason}")

@app.task
def run_daily_leadgen_job():
    logger.info("Starting daily leadgen job")
    asyncio.run(_run_async_job())
