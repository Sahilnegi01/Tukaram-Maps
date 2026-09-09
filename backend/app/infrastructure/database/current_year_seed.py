"""Idempotently add source-backed Maharashtra FDA actions reported in 2026."""
import asyncio
import hashlib
from datetime import date, datetime, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.domain.enums import ActionStatus, ActionType, CurrentStatus, EstablishmentType, SourceType
from app.domain.services.normalization import normalize_name
from app.infrastructure.database.models import (
    ActionModel, ArticleModel, EstablishmentModel, ProcessingStatus,
    SourceModel, action_articles,
)
from app.infrastructure.database.session import SessionFactory

ARTICLE_URL = "https://indianexpress.com/article/cities/mumbai/cockroaches-expired-food-fda-suspends-licences-of-restaurants-10807767/"
ARTICLE_TITLE = "Cockroaches, expired food: FDA action hits CCI, other top Mumbai clubs"

# Some coordinates are the named venue's OSM position; where OSM has no named
# feature, the published neighbourhood/club location is used and noted here.
RECORDS = [
    ("Cricket Club of India food establishments", "Cricket Club of India, Churchgate", 18.9319, 72.8246, ActionType.SHUT_DOWN,
     "FDA suspended affected food licences after reporting cockroaches, flies, mouldy vegetables, expired food and unsafe cold-room storage."),
    ("RK Juhu Gymkhana food establishment", "Juhu, Mumbai", 19.1075, 72.8263, ActionType.SHUT_DOWN,
     "FDA suspended the food licence after reporting poor hygiene facilities, improper raw-material cleaning and food handlers without protective clothing."),
    ("Aparna Juhu Gymkhana food establishment", "Juhu, Mumbai", 19.1078, 72.8270, ActionType.SHUT_DOWN,
     "FDA suspended the food licence after reporting rusted equipment, flies, non-food-grade packaging and failure to segregate food."),
    ("MIG Cricket Club food establishment", "Bandra East, Mumbai", 19.0578084, 72.8483095, ActionType.SHUT_DOWN,
     "FDA suspended the food licence after reporting an unauthorised operator, cockroach infestation, cross-contamination risk and missing mandatory records."),
    ("Willingdon Sports Club food establishment", "Haji Ali, Mumbai", 18.9763497, 72.8159490, ActionType.SHUT_DOWN,
     "FDA suspended the food licence after reporting unhygienic floors, deteriorating surfaces, poorly maintained drains and inadequate handler hygiene."),
    ("Goregaon Sports Club restaurant", "Goregaon Sports Club, Malad West", 19.1856296, 72.8335471, ActionType.SHUT_DOWN,
     "FDA issued a stop-business notice after finding the inspected restaurant operating without FSSAI registration or a licence."),
    ("Blue Resto", "Goregaon Sports Club, Malad West", 19.1858, 72.8335, ActionType.NOTICE_ISSUED,
     "FDA issued an improvement notice directing the restaurant to rectify deficiencies found during inspection."),
    ("Amar Tea", "Goregaon Sports Club, Malad West", 19.1856, 72.8333, ActionType.NOTICE_ISSUED,
     "FDA issued an improvement notice directing the establishment to rectify deficiencies found during inspection."),
    ("Cookie Dough Cafe", "Goregaon Sports Club, Malad West", 19.1854, 72.8336, ActionType.NOTICE_ISSUED,
     "FDA issued an improvement notice directing the cafe to rectify deficiencies found during inspection."),
    ("Bombay Gymkhana food establishment", "Fort, Mumbai", 18.9372, 72.8308, ActionType.NOTICE_ISSUED,
     "FDA issued an improvement notice directing the establishment to rectify deficiencies found during inspection."),
]


async def add_current_year_data():
    async with SessionFactory() as session:
        source = await session.scalar(select(SourceModel).where(SourceModel.domain == "indianexpress.com"))
        if not source:
            source = SourceModel(name="The Indian Express", domain="indianexpress.com", source_type=SourceType.NEWS,
                                 feed_url="https://indianexpress.com/section/cities/mumbai/feed/", state="Maharashtra")
            session.add(source)
            await session.flush()

        article = await session.scalar(select(ArticleModel).where(ArticleModel.canonical_url == ARTICLE_URL))
        if not article:
            summary = "FDA action followed July 27 inspections of food establishments at prominent Mumbai clubs."
            article = ArticleModel(source_id=source.id, title=ARTICLE_TITLE, normalized_title=normalize_name(ARTICLE_TITLE),
                url=ARTICLE_URL, canonical_url=ARTICLE_URL, url_hash=hashlib.sha256(ARTICLE_URL.encode()).hexdigest(),
                summary=summary, published_at=datetime(2026, 7, 28, 20, 24, 57, tzinfo=timezone.utc),
                content_hash=hashlib.sha256(summary.encode()).hexdigest(), processing_status=ProcessingStatus.PROCESSED)
            session.add(article)
            await session.flush()

        for name, address, lat, lng, action_type, reason in RECORDS:
            normalized = normalize_name(name)
            if await session.scalar(select(EstablishmentModel.id).where(EstablishmentModel.normalized_name == normalized)):
                continue
            establishment = EstablishmentModel(name=name, normalized_name=normalized, type=EstablishmentType.RESTAURANT,
                address=address, city="Mumbai", state="Maharashtra", latitude=lat, longitude=lng,
                location=WKTElement(f"POINT({lng} {lat})", srid=4326), current_status=CurrentStatus.UNKNOWN)
            session.add(establishment)
            await session.flush()
            action = ActionModel(establishment_id=establishment.id, action_type=action_type, reason=reason,
                authority="Maharashtra Food and Drug Administration", action_date=date(2026, 7, 27),
                status=ActionStatus.APPROVED, confidence_score=.96)
            session.add(action)
            await session.flush()
            await session.execute(action_articles.insert().values(action_id=action.id, article_id=article.id))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(add_current_year_data())
