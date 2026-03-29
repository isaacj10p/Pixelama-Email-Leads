from celery import Celery
from celery.schedules import crontab
from app.config import settings

app = Celery(
    "leadgen",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.scheduler.daily_job"]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=4,
)

app.conf.beat_schedule = {
    "daily-leadgen-job": {
        "task": "app.scheduler.daily_job.run_daily_leadgen_job",
        "schedule": crontab(hour=settings.JOB_SCHEDULE_HOUR, minute=0),
    }
}
