from datetime import datetime, timezone
import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.application.use_cases.reviews import ReviewService
from app.core.config import get_settings
from app.domain.enums import ActionStatus, CurrentStatus
from app.domain.services.confidence import ConfidenceService
from app.domain.services.filtering import is_relevant_candidate
from app.domain.services.matching import MatchingService
from app.domain.services.normalization import normalize_name
from app.infrastructure.ai.classifiers.strategies import RuleBasedArticleClassifier
from app.infrastructure.ai.extractors.rules import RuleEntityExtractor
from app.infrastructure.database.models import ActionModel, ArticleModel, EstablishmentModel, ProcessingStatus
from app.infrastructure.database.repositories import ReviewRequestRepository
log=structlog.get_logger()

class ProcessArticle:
    def __init__(self,session,classifier=None,extractor=None):
        self.session=session; self.classifier=classifier or RuleBasedArticleClassifier(); self.extractor=extractor or RuleEntityExtractor()
    async def execute(self,article_id):
        article=await self.session.scalar(select(ArticleModel).where(ArticleModel.id==article_id).options(selectinload(ArticleModel.actions)))
        if not article or article.processing_status in (ProcessingStatus.PROCESSED,ProcessingStatus.REJECTED): return {"status":"unchanged"}
        article.processing_status=ProcessingStatus.PROCESSING; text=f"{article.title}. {article.summary or ''}"
        if not is_relevant_candidate(text): article.processing_status=ProcessingStatus.REJECTED; await self.session.commit(); return {"status":"regex_rejected"}
        classification=self.classifier.classify(text)
        if not classification.is_relevant: article.processing_status=ProcessingStatus.REJECTED; await self.session.commit(); return {"status":"classifier_rejected"}
        entity=self.extractor.extract(text)
        if not entity.get("establishment_name") or not entity.get("city"): article.processing_status=ProcessingStatus.REJECTED; await self.session.commit(); return {"status":"insufficient_entities"}
        normalized=normalize_name(entity["establishment_name"])
        establishment=await self.session.scalar(select(EstablishmentModel).where(EstablishmentModel.normalized_name==normalized,EstablishmentModel.city.ilike(entity["city"]),EstablishmentModel.state.ilike(entity["state"] or "%")).options(selectinload(EstablishmentModel.actions).selectinload(ActionModel.articles)))
        new_establishment=establishment is None
        if new_establishment:
            establishment=EstablishmentModel(name=entity["establishment_name"],normalized_name=normalized,type=entity["establishment_type"],city=entity["city"],state=entity["state"] or "UNKNOWN",current_status=CurrentStatus.UNKNOWN);self.session.add(establishment);await self.session.flush()
        incoming={"establishment_id":establishment.id,"action_type":entity["action_type"],"authority":entity.get("authority"),"reason":entity.get("reason"),"action_date":entity.get("action_date")}
        action=next((a for a in establishment.actions if MatchingService().same_action(incoming,{"establishment_id":a.establishment_id,"action_type":a.action_type,"authority":a.authority,"reason":a.reason,"action_date":a.action_date})),None)
        score=ConfidenceService().calculate(relevance=classification.confidence,establishment=.55 if new_establishment else .98,action=.9 if entity["action_type"].value!="OTHER" else .3,action_match=.95 if action else .55,date=.5,authority=.5,source=.9)
        disposition=ConfidenceService().disposition(score,get_settings().auto_approval_threshold,get_settings().review_threshold)
        if not action:
            action=ActionModel(establishment_id=establishment.id,action_type=entity["action_type"],status=ActionStatus(disposition),confidence_score=score,articles=[article]);self.session.add(action);await self.session.flush()
        elif article not in action.articles: action.articles.append(article)
        if entity.get("current_status_signal")=="OPEN" and disposition=="APPROVED": establishment.current_status=CurrentStatus.OPEN
        article.processing_status=ProcessingStatus.PROCESSED
        token=None
        if action.status==ActionStatus.PENDING_REVIEW:
            review,token=await ReviewService(self.session,ReviewRequestRepository(self.session)).create(action.id)
        await self.session.commit(); await log.ainfo("article_processed",article_id=str(article.id),establishment_id=str(establishment.id),action_id=str(action.id),confidence=score,status=disposition)
        return {"status":disposition,"action_id":str(action.id),"review_token":token}
