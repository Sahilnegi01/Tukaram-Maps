"""Replace the development-only dataset with a small source-backed dataset."""
import asyncio
import hashlib
from datetime import date, datetime, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy import delete, func, select

from app.domain.enums import ActionStatus, ActionType, CurrentStatus, EstablishmentType, SourceType
from app.domain.services.normalization import normalize_name
from app.infrastructure.database.models import (
    ActionModel, ArticleModel, EstablishmentModel, ProcessingStatus,
    ReviewRequestModel, SourceModel, action_articles,
)
from app.infrastructure.database.session import SessionFactory

REPORT_URL = "https://indianexpress.com/article/cities/mumbai/fda-suspends-six-mumbai-eateries-hygiene-crackdown-10764532/"
POORNIMA_URL = "https://indianexpress.com/article/cities/mumbai/fda-suspends-license-mumbais-six-decade-old-udupi-eatery-poornima-restaurant-10806651/"
FOLLOW_UP_URL = "https://indianexpress.com/article/cities/mumbai/why-bombay-courts-are-reversing-fdas-tukaram-mundhe-instant-restaurant-closure-orders-10815461/"

RECORDS = [
    ("Flint & Waarsa", "NCPA, Nariman Point", 18.9251593, 72.8205615, date(2026, 6, 27),
     "FDA inspectors reported misbranded products and expired food items; its food licence was suspended."),
    ("M.K. Bakery", "Borivali East", 19.2187187, 72.8654856, None,
     "FDA inspectors reported food production during renovation, unhygienic premises and labelling violations; its food licence was suspended."),
    ("Hotel Shree Krishna (Sujit Bar and Restaurant)", "Bhandup West", 19.1462636, 72.9339461, None,
     "FDA inspectors reported defective refrigeration and poor hygiene; its food licence was suspended."),
    ("Hotel Gopal Krishna", "Santacruz East", 19.0740097, 72.8689943, None,
     "FDA inspectors reported a rat, foul kitchen odour and garbage in drainage lines; its food licence was suspended."),
    ("Karak Enterprises Pvt Ltd", "Andheri East", 19.1158835, 72.8542020, None,
     "FDA inspectors reported cockroach infestation, unsafe refrigeration and other hygiene failures; its food licence was suspended."),
    ("Madras Diaries", "28th Road, Bandra West", 19.0598965, 72.8339617, None,
     "FDA inspectors reported hygiene failures and missing food-testing and statutory records; its food licence was suspended."),
]


def make_article(source_id, title, url, summary, published):
    return ArticleModel(
        source_id=source_id, title=title, normalized_title=normalize_name(title),
        url=url, canonical_url=url, url_hash=hashlib.sha256(url.encode()).hexdigest(),
        summary=summary, published_at=published,
        content_hash=hashlib.sha256(summary.encode()).hexdigest(),
        processing_status=ProcessingStatus.PROCESSED,
    )


async def replace_demo_data():
    async with SessionFactory() as session:
        total = await session.scalar(select(func.count()).select_from(ArticleModel))
        demo = await session.scalar(select(func.count()).select_from(ArticleModel).where(ArticleModel.url.like("https://example.test/%")))
        if total and total != demo:
            raise RuntimeError("Refusing to replace a database containing non-demo articles")

        await session.execute(delete(ReviewRequestModel))
        await session.execute(delete(action_articles))
        await session.execute(delete(ActionModel))
        await session.execute(delete(ArticleModel))
        await session.execute(delete(EstablishmentModel))
        await session.execute(delete(SourceModel))

        source = SourceModel(
            name="The Indian Express", domain="indianexpress.com",
            source_type=SourceType.NEWS,
            feed_url="https://indianexpress.com/section/cities/mumbai/feed/",
            state="Maharashtra",
        )
        session.add(source)
        await session.flush()

        report = make_article(
            source.id,
            "Rats, cockroaches, rotting food: FDA suspends six Mumbai eateries in hygiene crackdown",
            REPORT_URL,
            "Maharashtra FDA suspended six Mumbai food licences after inspections from June 26 to June 28, 2026.",
            datetime(2026, 6, 30, 15, 55, 23, tzinfo=timezone.utc),
        )
        session.add(report)
        await session.flush()

        for name, address, lat, lng, action_date, reason in RECORDS:
            establishment = EstablishmentModel(
                name=name, normalized_name=normalize_name(name),
                type=EstablishmentType.RESTAURANT, address=address,
                city="Mumbai", state="Maharashtra", latitude=lat, longitude=lng,
                location=WKTElement(f"POINT({lng} {lat})", srid=4326),
                current_status=CurrentStatus.UNKNOWN,
            )
            session.add(establishment)
            await session.flush()
            action = ActionModel(
                establishment_id=establishment.id, action_type=ActionType.SHUT_DOWN,
                reason=reason, authority="Maharashtra Food and Drug Administration",
                action_date=action_date, status=ActionStatus.APPROVED,
                confidence_score=.95,
            )
            session.add(action)
            await session.flush()
            await session.execute(action_articles.insert().values(action_id=action.id, article_id=report.id))

        poornima = EstablishmentModel(
            name="Poornima Restaurant", normalized_name=normalize_name("Poornima Restaurant"),
            type=EstablishmentType.RESTAURANT, address="Raja Bahadur Compound, Fort",
            city="Mumbai", state="Maharashtra", latitude=18.9308002, longitude=72.8335262,
            location=WKTElement("POINT(72.8335262 18.9308002)", srid=4326),
            current_status=CurrentStatus.OPEN,
        )
        session.add(poornima)
        await session.flush()
        suspension_article = make_article(
            source.id, "FDA suspends license of Mumbai's six-decade-old Udupi eatery Poornima Restaurant",
            POORNIMA_URL, "FDA suspended Poornima Restaurant's licence after a July 23 inspection reported food-safety and hygiene violations.",
            datetime(2026, 7, 28, 10, 21, 11, tzinfo=timezone.utc),
        )
        follow_up = make_article(
            source.id, "Why Bombay courts are reversing FDA's instant restaurant closure orders",
            FOLLOW_UP_URL, "FDA told the Bombay High Court that Poornima's suspension would be treated as an improvement notice pending reinspection.",
            datetime(2026, 8, 3, 11, 20, 11, tzinfo=timezone.utc),
        )
        session.add_all([suspension_article, follow_up])
        await session.flush()
        actions = [
            ActionModel(establishment_id=poornima.id, action_type=ActionType.SHUT_DOWN,
                reason="FDA reported fungal growth, flies, stagnant water, dirty drains and unsafe food storage.",
                authority="Maharashtra Food and Drug Administration", action_date=date(2026, 7, 23),
                status=ActionStatus.APPROVED, confidence_score=.98),
            ActionModel(establishment_id=poornima.id, action_type=ActionType.REOPENED,
                reason="FDA agreed to treat the suspension as an improvement notice and reinspect after rectification.",
                authority="Bombay High Court / Maharashtra Food and Drug Administration", action_date=date(2026, 7, 31),
                status=ActionStatus.APPROVED, confidence_score=.95),
        ]
        session.add_all(actions)
        await session.flush()
        await session.execute(action_articles.insert().values(action_id=actions[0].id, article_id=suspension_article.id))
        await session.execute(action_articles.insert().values(action_id=actions[1].id, article_id=follow_up.id))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(replace_demo_data())
