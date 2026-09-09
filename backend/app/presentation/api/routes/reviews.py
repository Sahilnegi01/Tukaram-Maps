from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.use_cases.reviews import ReviewService
from app.infrastructure.database.repositories import ReviewRequestRepository
from app.presentation.api.dependencies import session_dep
router=APIRouter()
def payload(r):
    a=r.action; e=a.establishment
    return {"id":str(r.id),"status":r.status,"expires_at":r.expires_at,"establishment":{"name":e.name,"type":e.type,"city":e.city,"state":e.state},"action":{"type":a.action_type,"date":a.action_date,"authority":a.authority,"reason":a.reason,"confidence":a.confidence_score},"articles":[{"source":x.source.name,"title":x.title,"url":x.url,"published_at":x.published_at} for x in a.articles]}
@router.get("/reviews/{token}")
async def get_review(token: str, session: AsyncSession=Depends(session_dep)):
    return {"data":payload(await ReviewService(session,ReviewRequestRepository(session)).get(token))}
@router.post("/reviews/{token}/approve")
async def approve(token: str, session: AsyncSession=Depends(session_dep)):
    return {"data":{"status":(await ReviewService(session,ReviewRequestRepository(session)).decide(token,True)).status}}
@router.post("/reviews/{token}/reject")
async def reject(token: str, session: AsyncSession=Depends(session_dep)):
    return {"data":{"status":(await ReviewService(session,ReviewRequestRepository(session)).decide(token,False)).status}}

