import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
from app.core.exceptions import InvalidReviewToken, ReviewExpired, ReviewProcessed
from app.domain.enums import ActionStatus, ReviewStatus
from app.infrastructure.database.models import ReviewRequestModel

def token_hash(token): return hashlib.sha256(token.encode()).hexdigest()

class ReviewService:
    def __init__(self, session, repository): self.session, self.repository = session, repository
    async def create(self, action_id):
        token = secrets.token_urlsafe(32)
        review = ReviewRequestModel(action_id=action_id, token_hash=token_hash(token), expires_at=datetime.now(timezone.utc)+timedelta(hours=get_settings().review_token_ttl_hours))
        self.session.add(review)
        await self.session.flush()
        return review, token
    async def get(self, token, require_pending=False):
        review = await self.repository.by_hash(token_hash(token))
        if not review: raise InvalidReviewToken("Invalid review link.")
        if review.expires_at <= datetime.now(timezone.utc):
            if review.status == ReviewStatus.PENDING: review.status = ReviewStatus.EXPIRED
            raise ReviewExpired("This review request has expired.")
        if require_pending and review.status != ReviewStatus.PENDING: raise ReviewProcessed("This review request has already been processed.")
        return review
    async def decide(self, token, approve):
        try:
            review = await self.get(token, require_pending=True)
            review.status = ReviewStatus.APPROVED if approve else ReviewStatus.REJECTED
            review.action.status = ActionStatus.APPROVED if approve else ActionStatus.REJECTED
            review.reviewed_at = datetime.now(timezone.utc)
            await self.session.commit()
            return review
        except Exception:
            await self.session.rollback(); raise

