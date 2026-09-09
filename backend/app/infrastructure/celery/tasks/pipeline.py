import asyncio
from app.application.services.ingestion import NewsIngestionService
from app.application.use_cases.process_article import ProcessArticle
from app.infrastructure.celery.celery_app import celery_app
from app.infrastructure.database.session import SessionFactory
async def _fetch():
    async with SessionFactory() as session: return [str(x) for x in await NewsIngestionService(session).fetch_all()]
@celery_app.task(name="fetch_all_news_sources",autoretry_for=(TimeoutError,ConnectionError),retry_backoff=True,retry_jitter=True,max_retries=5)
def fetch_all_news_sources():
    ids=asyncio.run(_fetch())
    for article_id in ids: process_article.delay(article_id)
    return ids
@celery_app.task(name="process_article",autoretry_for=(TimeoutError,ConnectionError),retry_backoff=True,max_retries=3)
def process_article(article_id):
    async def run():
        async with SessionFactory() as session: return await ProcessArticle(session).execute(article_id)
    result=asyncio.run(run())
    if result.get("review_token"): send_review_email.delay(result["action_id"],result.pop("review_token"))
    return result
@celery_app.task(name="classify_article")
def classify_article(article_id): return article_id
@celery_app.task(name="extract_entities")
def extract_entities(article_id): return article_id
@celery_app.task(name="match_establishment")
def match_establishment(article_id): return article_id
@celery_app.task(name="match_action")
def match_action(article_id): return article_id
@celery_app.task(name="calculate_confidence")
def calculate_confidence(article_id): return article_id
@celery_app.task(name="create_review_request")
def create_review_request(action_id): return action_id
@celery_app.task(name="send_review_email",autoretry_for=(ConnectionError,),retry_backoff=True,max_retries=5)
def send_review_email(action_id,token):
    from app.core.config import get_settings
    from app.infrastructure.email.service import SMTPEmailService
    s=get_settings(); url=f"{s.frontend_url}/review/{token}"
    asyncio.run(SMTPEmailService().send_review(s.review_email,"Enforcement action review",f'<p>An action requires review.</p><p><a href="{url}">Review Action</a></p>'))
    return action_id
@celery_app.task(name="update_establishment_status")
def update_establishment_status(establishment_id,status): return {"id":establishment_id,"status":status}
