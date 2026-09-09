from sqlalchemy import cast, exists, func, select
from geoalchemy2 import Geometry
from sqlalchemy.orm import selectinload
from app.domain.enums import ActionStatus, CurrentStatus
from app.infrastructure.database.models import ActionModel, ArticleModel, EstablishmentModel

class PublicQueryService:
    def __init__(self, session): self.session = session
    def qualifying(self):
        evidence = exists(select(1).select_from(ActionModel).join(ActionModel.articles).where(ActionModel.establishment_id == EstablishmentModel.id, ActionModel.status == ActionStatus.APPROVED))
        return select(EstablishmentModel).where(evidence)
    async def map(self, params):
        q = self.qualifying().options(selectinload(EstablishmentModel.actions).selectinload(ActionModel.articles))
        if None not in (params.north, params.south, params.east, params.west):
            envelope = func.ST_MakeEnvelope(params.west, params.south, params.east, params.north, 4326)
            q = q.where(func.ST_Intersects(cast(EstablishmentModel.location, Geometry(srid=4326)), envelope))
        if params.state: q=q.where(EstablishmentModel.state.ilike(params.state))
        if params.city: q=q.where(EstablishmentModel.city.ilike(params.city))
        if params.type: q=q.where(EstablishmentModel.type == params.type)
        if params.current_status: q=q.where(EstablishmentModel.current_status == params.current_status)
        if params.action_type or params.from_date or params.to_date:
            q=q.join(ActionModel).where(ActionModel.status == ActionStatus.APPROVED)
            if params.action_type: q=q.where(ActionModel.action_type == params.action_type)
            if params.from_date: q=q.where(ActionModel.action_date >= params.from_date)
            if params.to_date: q=q.where(ActionModel.action_date <= params.to_date)
        rows=list((await self.session.scalars(q.distinct())).unique().all())
        return rows
