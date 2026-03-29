import dns.resolver
import aiosmtplib
import random
import httpx
from typing import List, Optional, Tuple
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.domain import MXCache, DomainPattern
from app.config import settings

class EmailFinder:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.smtplib_kwargs = {
            "timeout": 8,
        }
        self.mail_from_rotations = [
            "verify@gmail.com",
            "check@yahoo.com",
            "test@outlook.com"
        ]
        
    def generate_variants(self, first: str, last: str, domain: str) -> List[str]:
        f = first[0] if first else ""
        l = last[0] if last else ""
        
        variants = [
            f"{first}.{last}@{domain}",
            f"{first}{last}@{domain}",
            f"{f}{last}@{domain}",
            f"{first}@{domain}",
            f"{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{first}-{last}@{domain}",
            f"{last}.{first}@{domain}",
            f"{f}.{last}@{domain}",
            f"{first}.{l}@{domain}",
            f"info@{domain}",
            f"contacto@{domain}",
            f"hola@{domain}"
        ]
        return [v.lower() for v in variants if '@' in v and len(v) > len(f"@{domain}")]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    async def resolve_mx(self, domain: str) -> Optional[str]:
        stmt = select(MXCache).where(MXCache.domain == domain)
        res = await self.db.execute(stmt)
        cached = res.scalars().first()
        
        if cached:
            return cached.mx_host
            
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            mx_record = sorted(answers, key=lambda x: x.preference)[0].exchange.to_text().rstrip('.')
            
            new_cache = MXCache(domain=domain, mx_host=mx_record)
            self.db.add(new_cache)
            await self.db.commit()
            
            return mx_record
        except Exception as e:
            logger.warning(f"DNS resolution failed for {domain}: {e}")
            return None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=10))
    async def verify_smtp(self, email: str, mx_host: str) -> Tuple[bool, bool]:
        """Returns (is_valid, is_catchall)"""
        domain = email.split('@')[1]
        catchall_email = f"catchall_test_{random.randint(100000, 999999)}@{domain}"
        mail_from = random.choice(self.mail_from_rotations)
        
        smtp = aiosmtplib.SMTP(hostname=mx_host, port=25, **self.smtplib_kwargs)
        
        try:
            await smtp.connect()
            await smtp.ehlo(hostname=settings.SMTP_EHLO_DOMAIN)
        
            # Test Catchall
            try:
                await smtp.mail(mail_from)
                code, msg = await smtp.rcpt(catchall_email)
                if code == 250:
                    await smtp.quit()
                    return (True, True) # Is catch-all
            except Exception:
                pass # Continue to actual check
                
            # Test actual email
            await smtp.mail(mail_from)
            code, msg = await smtp.rcpt(email)
            await smtp.quit()
            
            return (code == 250, False)
            
        except Exception as e:
            logger.warning(f"SMTP verification failed for {email} on {mx_host}: {e}")
            raise e
        finally:
            if smtp.is_connected:
                await smtp.quit()
                
    async def fallback_api_check(self, email: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                res = await client.get(f"https://www.disify.com/api/email/{email}")
                if res.status_code == 200:
                    data = res.json()
                    return not data.get('disposable', True) and data.get('dns', False)
        except Exception as e:
            logger.error(f"Fallback API failed for {email}: {e}")
        return False
