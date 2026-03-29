from pydantic_settings import BaseSettings
from typing import List, Dict
import json

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@postgres:5432/leadgen"
    REDIS_URL: str = "redis://redis:6379/0"
    API_KEY: str = "change_me_in_production"
    
    IG_ACCOUNTS: str = "[]"
    LOG_LEVEL: str = "INFO"
    
    JOB_MAX_MINUTES: int = 28
    JOB_TARGET_LEADS: int = 1200
    JOB_SCHEDULE_HOUR: int = 3
    SMTP_EHLO_DOMAIN: str = "gmail.com"
    MIN_SCORE_THRESHOLD: int = 40

    @property
    def ig_accounts_list(self) -> List[Dict[str, str]]:
        try:
            return json.loads(self.IG_ACCOUNTS)
        except json.JSONDecodeError:
            return []

    class Config:
        env_file = ".env"

settings = Settings()
