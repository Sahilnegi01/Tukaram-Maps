from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.use_cases.public import PublicQueryService
from app.core.exceptions import NotFoundError
from app.domain.enums import ActionStatus, ActionType, CurrentStatus
from app.infrastructure.database.models import ActionModel, EstablishmentModel
from app.infrastructure.database.repositories import EstablishmentRepository
from app.presentation.api.dependencies import session_dep
from app.presentation.api.schemas.public import MapParams
router=APIRouter()
def article_json(a): return {"source":a.source.name,"title":a.title,"published_at":a.published_at,"summary":a.summary,"url":a.url}
def action_json(a): return {"id":str(a.id),"type":a.action_type,"date":a.action_date,"authority":a.authority,"reason":a.reason,"confidence":a.confidence_score,"articles":[article_json(x) for x in a.articles]}
@router.get("/map/establishments")
async def map_establishments(params: MapParams=Depends(), session: AsyncSession=Depends(session_dep)):
    rows=await PublicQueryService(session).map(params); data=[]
    if params.zoom <= 6:
        buckets={}
        for e in rows:
            key=(round(e.latitude or 0),round(e.longitude or 0)); buckets.setdefault(key,[]).append(e)
        clusters=[{"cluster":True,"id":f"cluster-{lat}-{lng}","latitude":sum(e.latitude for e in group)/len(group),"longitude":sum(e.longitude for e in group)/len(group),"count":len(group)} for (lat,lng),group in buckets.items()]
        return {"data":clusters,"meta":{"zoom":params.zoom,"clustered":True}}
    for e in rows:
        approved=[a for a in e.actions if a.status == ActionStatus.APPROVED and a.articles]
        latest=max(approved,key=lambda a:a.action_date or a.created_at.date())
        data.append({"id":str(e.id),"name":e.name,"type":e.type,"city":e.city,"state":e.state,"latitude":e.latitude,"longitude":e.longitude,"current_status":e.current_status,"latest_action":{"type":latest.action_type,"date":latest.action_date}})
    return {"data":data,"meta":{"zoom":params.zoom,"clustered":False}}
@router.get("/map/overview")
async def map_overview(session: AsyncSession=Depends(session_dep)):
    approved = ActionModel.status == ActionStatus.APPROVED
    action_count = await session.scalar(select(func.count()).select_from(ActionModel).where(approved))
    warning_count = await session.scalar(select(func.count()).select_from(ActionModel).where(approved, ActionModel.action_type == ActionType.NOTICE_ISSUED))
    suspended_count = await session.scalar(select(func.count()).select_from(ActionModel).where(approved, ActionModel.action_type.in_([ActionType.SHUT_DOWN, ActionType.LICENSE_CANCELLED])))
    open_count = await session.scalar(select(func.count()).select_from(EstablishmentModel).where(EstablishmentModel.current_status == CurrentStatus.OPEN))
    return {"data":{"actions":action_count,"warnings":warning_count,"suspended":suspended_count,"open":open_count}}
@router.get("/establishments/search")
async def search(q: str=Query(min_length=2,max_length=100), session: AsyncSession=Depends(session_dep)):
    rows=await EstablishmentRepository(session).search(q)
    return {"data":[{"id":str(e.id),"name":e.name,"city":e.city,"state":e.state,"latitude":e.latitude,"longitude":e.longitude} for e in rows]}
@router.get("/establishments/{entity_id}")
async def details(entity_id: str, session: AsyncSession=Depends(session_dep)):
    e=await EstablishmentRepository(session).get(entity_id)
    if not e: raise NotFoundError("Establishment not found.")
    approved=sorted((a for a in e.actions if a.status == ActionStatus.APPROVED and a.articles),key=lambda a:a.action_date or a.created_at.date(),reverse=True)
    return {"data":{"id":str(e.id),"name":e.name,"type":e.type,"current_status":e.current_status,"address":e.address,"city":e.city,"state":e.state,"latitude":e.latitude,"longitude":e.longitude,"actions":[action_json(a) for a in approved]}}
