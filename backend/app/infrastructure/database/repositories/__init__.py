from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from app.domain.enums import ActionStatus, CurrentStatus
from app.infrastructure.database.models import ActionModel, ArticleModel, EstablishmentModel, ReviewRequestModel, SourceModel

class EstablishmentRepository:
    def __init__(self, session): self.session = session
    async def get(self, entity_id):
        return await self.session.scalar(select(EstablishmentModel).where(EstablishmentModel.id == entity_id).options(selectinload(EstablishmentModel.actions).selectinload(ActionModel.articles).selectinload(ArticleModel.source)))
    async def search(self, q, limit=20):
        term = f"%{q.strip()}%"
        verified=select(ActionModel.id).join(ActionModel.articles).where(ActionModel.establishment_id==EstablishmentModel.id,ActionModel.status==ActionStatus.APPROVED).exists()
        return list((await self.session.scalars(select(EstablishmentModel).where(EstablishmentModel.current_status==CurrentStatus.OPEN,verified,or_(EstablishmentModel.city.ilike(term), EstablishmentModel.state.ilike(term), EstablishmentModel.name.ilike(term))).limit(limit))).all())
class ActionRepository:
    def __init__(self, session): self.session = session
    async def get(self, entity_id): return await self.session.get(ActionModel, entity_id)
class ArticleRepository:
    def __init__(self, session): self.session = session
    async def find_duplicate(self, canonical_url, content_hash=None):
        conditions = [ArticleModel.canonical_url == canonical_url]
        if content_hash: conditions.append(ArticleModel.content_hash == content_hash)
        return await self.session.scalar(select(ArticleModel).where(or_(*conditions)))
class SourceRepository:
    def __init__(self, session): self.session = session
    async def enabled(self): return list((await self.session.scalars(select(SourceModel).where(SourceModel.enabled.is_(True)))).all())
class ReviewRequestRepository:
    def __init__(self, session): self.session = session
    async def by_hash(self, token_hash):
        return await self.session.scalar(select(ReviewRequestModel).where(ReviewRequestModel.token_hash == token_hash).options(selectinload(ReviewRequestModel.action).selectinload(ActionModel.establishment), selectinload(ReviewRequestModel.action).selectinload(ActionModel.articles).selectinload(ArticleModel.source)))
