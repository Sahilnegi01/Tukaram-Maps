import hashlib
from datetime import datetime, timezone
import structlog
from sqlalchemy import select
from app.domain.services.normalization import normalize_name, normalize_url
from app.infrastructure.database.models import ArticleModel, ProcessingStatus
from app.infrastructure.database.repositories import ArticleRepository, SourceRepository
from app.infrastructure.news.factory import NewsSourceFactory
log=structlog.get_logger()
class NewsIngestionService:
    def __init__(self,session): self.session=session
    async def fetch_all(self):
        sources=await SourceRepository(self.session).enabled(); created=[]
        for source in sources:
            try:
                await log.ainfo("source_fetch_started",source_id=str(source.id))
                items=await NewsSourceFactory.create(source).fetch_feed_items()
                for item in items:
                    canonical=normalize_url(item.url); url_hash=hashlib.sha256(canonical.encode()).hexdigest()
                    if await ArticleRepository(self.session).find_duplicate(canonical):
                        await log.ainfo("duplicate_article",source_id=str(source.id),url_hash=url_hash); continue
                    article=ArticleModel(source_id=source.id,title=item.title,normalized_title=normalize_name(item.title),url=item.url,canonical_url=canonical,url_hash=url_hash,summary=(item.summary or "")[:600],published_at=item.published_at,processing_status=ProcessingStatus.NEW)
                    self.session.add(article); await self.session.flush(); created.append(article.id)
                source.last_successful_fetch=datetime.now(timezone.utc); source.consecutive_failures=0; source.last_error=None
                await self.session.commit(); await log.ainfo("source_fetch_success",source_id=str(source.id),articles=len(created))
            except Exception as exc:
                await self.session.rollback(); source.last_failed_fetch=datetime.now(timezone.utc); source.consecutive_failures+=1; source.last_error=str(exc)[:1000]; await self.session.commit()
                await log.aerror("source_fetch_failed",source_id=str(source.id),error=type(exc).__name__)
        return created

