from fastapi import APIRouter, Depends
import hashlib, secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.enums import ReviewStatus
from app.infrastructure.database.models import ActionModel, ArticleModel, ReviewRequestModel
from app.presentation.api.dependencies import internal_auth, session_dep
from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ReviewProcessed
router=APIRouter(dependencies=[Depends(internal_auth)])
@router.get("/internal/reviews")
async def pending_reviews(session: AsyncSession=Depends(session_dep)):
    q=select(ReviewRequestModel).where(ReviewRequestModel.status==ReviewStatus.PENDING).options(selectinload(ReviewRequestModel.action).selectinload(ActionModel.establishment),selectinload(ReviewRequestModel.action).selectinload(ActionModel.articles).selectinload(ArticleModel.source))
    rows=list((await session.scalars(q)).all())
    return {"data":[{"id":str(r.id),"establishment":r.action.establishment.name,"city":r.action.establishment.city,"state":r.action.establishment.state,"action":r.action.action_type,"date":r.action.action_date,"confidence":r.action.confidence_score,"sources":[x.source.name for x in r.action.articles],"status":r.status} for r in rows]}
@router.post("/internal/reviews/{review_id}/access-link")
async def review_access_link(review_id: str,session: AsyncSession=Depends(session_dep)):
    review=await session.get(ReviewRequestModel,review_id)
    if not review: raise NotFoundError("Review not found.")
    if review.status!=ReviewStatus.PENDING: raise ReviewProcessed("This review request has already been processed.")
    token=secrets.token_urlsafe(32);review.token_hash=hashlib.sha256(token.encode()).hexdigest();review.expires_at=datetime.now(timezone.utc)+timedelta(hours=get_settings().review_token_ttl_hours);await session.commit()
    return {"data":{"path":f"/review/{token}"}}
