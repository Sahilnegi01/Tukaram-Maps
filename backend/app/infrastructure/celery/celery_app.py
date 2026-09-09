from celery import Celery
from app.core.config import get_settings
s=get_settings(); celery_app=Celery("enforcement",broker=s.redis_url,backend=s.redis_url,include=["app.infrastructure.celery.tasks.pipeline"])
celery_app.conf.update(task_serializer="json",accept_content=["json"],result_serializer="json",timezone="UTC",beat_schedule={"poll-rss-feeds":{"task":"fetch_all_news_sources","schedule":s.news_poll_interval_minutes*60}},task_acks_late=True)

