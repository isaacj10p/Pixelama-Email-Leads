import random
import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from loguru import logger
from playwright.async_api import async_playwright, Browser, Page, Playwright
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.profile import Profile
from app.models.seed import SeedAccount
from app.models.session import IGSession
from app.utils.proxy_manager import ProxyManager
from app.config import settings
from app.exceptions import RateLimitException, ProxyException, ScraperException
from app.enrichment.classifier import Classifier

# This is a stub implementation highlighting the core playwright architecture.
# An actual Instagram scraper involves more complex selector discovery and persistence.

class InstagramScraper:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.proxy_manager = ProxyManager(db)
        self.classifier = Classifier()
        
    async def _get_ig_session(self) -> dict:
        stmt = select(IGSession).where(IGSession.is_healthy == True).order_by(IGSession.last_used.asc().nullsfirst())
        result = await self.db.execute(stmt)
        session_record = result.scalars().first()
        
        if session_record and session_record.cookies_json:
            session_record.last_used = datetime.now(timezone.utc)
            await self.db.commit()
            return {"username": session_record.username, "cookies": json.loads(session_record.cookies_json)}
            
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    async def scrape_followers(self, seed_account: SeedAccount, limit: int = 200) -> List[str]:
        logger.info(f"Scraping followers for {seed_account.username}")
        # Note: True scraping involves locating the followers dialog, scrolling, and extracting links
        await asyncio.sleep(random.uniform(2.5, 6.0))
        # Simulated extraction
        return [f"follower_{random.randint(1000, 9999)}" for _ in range(min(10, limit))]

    async def scrape_profile(self, page: Page, username: str) -> Optional[dict]:
        logger.info(f"Scraping profile {username}")
        
        try:
            await page.goto(f"https://www.instagram.com/{username}/", timeout=15000)
            await asyncio.sleep(random.uniform(2.5, 6.0))
            
            # Check for Rate Limit page
            content = await page.content()
            if "Try Again Later" in content or "We restrict certain activity" in content:
                raise RateLimitException("Instagram rate limit detected on profile load.")

            # Simulated successful extraction
            data = {
                "username": username,
                "full_name": f"Business {username}",
                "biography": "We are a local dental clinic with 10 years of experience. Call us!",
                "external_url": None, # Test empty url scenario
                "follower_count": random.randint(300, 5000),
                "following_count": 100,
                "post_count": 50,
                "is_business_account": True,
                "business_category_name": "Dentist",
                "business_email": "info@dentaltest.com",
                "business_phone": "+34600000000",
                "ig_profile_url": f"https://instagram.com/{username}/"
            }
            return data
            
        except RateLimitException as e:
            raise e
        except Exception as e:
            logger.error(f"Error scraping profile {username}: {e}")
            return None

    async def save_profile(self, data: dict):
        if not data:
            return
            
        stmt = select(Profile).where(Profile.username == data['username'])
        result = await self.db.execute(stmt)
        profile = result.scalars().first()
        
        now = datetime.now(timezone.utc)
        
        # Classification
        classification = self.classifier.classify(data)
        
        if profile:
            # Update criteria
            if profile.last_scraped and (now - profile.last_scraped) < timedelta(days=7):
                return # Skip update
        else:
            profile = Profile(username=data['username'])
            self.db.add(profile)
            
        profile.full_name = data.get('full_name')
        profile.biography = data.get('biography')
        profile.external_url = data.get('external_url')
        profile.follower_count = data.get('follower_count', 0)
        profile.following_count = data.get('following_count', 0)
        profile.post_count = data.get('post_count', 0)
        profile.is_business_account = data.get('is_business_account', False)
        profile.business_category_name = data.get('business_category_name')
        profile.business_email = data.get('business_email')
        profile.business_phone = data.get('business_phone')
        profile.ig_profile_url = data.get('ig_profile_url')
        
        profile.lead_score = classification['score']
        profile.detected_category = classification['category']
        profile.personalization_context = classification['context']
        profile.has_website = bool(data.get('external_url'))
        
        profile.last_scraped = now
        await self.db.commit()

    async def run_extraction_for_seed(self, seed: SeedAccount):
        proxy = await self.proxy_manager.get_next_proxy()
        
        logger.info(f"Starting extraction for seed {seed.username} using proxy {proxy.proxy_url}")
        
        async with async_playwright() as p:
            # Apply SOCKS5 Proxy
            browser_args = {}
            if proxy:
                browser_args["proxy"] = {"server": proxy.proxy_url}
                
            browser = await p.chromium.launch(headless=True, **browser_args)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Simulated Cookie injection
            ig_sess = await self._get_ig_session()
            if ig_sess:
                await context.add_cookies(ig_sess['cookies'])
                
            page = await context.new_page()
            
            try:
                followers = await self.scrape_followers(seed, limit=50) # Bounded for batch testing
                
                profiles_scraped_in_session = 0
                
                for follower_username in followers:
                    if profiles_scraped_in_session >= 200:
                        logger.warning("Session limit reached (200). Rotating session.")
                        break
                        
                    profile_data = await self.scrape_profile(page, follower_username)
                    if profile_data:
                        await self.save_profile(profile_data)
                        profiles_scraped_in_session += 1
                        
                await self.proxy_manager.mark_success(proxy.id)
                
            except RateLimitException as e:
                logger.error(f"Rate limited on proxy {proxy.proxy_url}. {e}")
                await self.proxy_manager.mark_failure(proxy.id)
                # Pause logic handled by caller or retry decorator
                await asyncio.sleep(60) # Minimal manual pause
                
            finally:
                await browser.close()
