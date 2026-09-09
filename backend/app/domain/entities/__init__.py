from dataclasses import dataclass, field
from datetime import date
from uuid import UUID
from app.domain.enums import ActionStatus, ActionType, CurrentStatus, EstablishmentType

@dataclass
class Establishment:
    name: str; type: EstablishmentType; city: str; state: str
    current_status: CurrentStatus = CurrentStatus.UNKNOWN
    id: UUID | None = None; address: str | None = None; latitude: float | None = None; longitude: float | None = None

@dataclass
class Action:
    establishment_id: UUID; action_type: ActionType; status: ActionStatus = ActionStatus.PENDING_REVIEW
    id: UUID | None = None; reason: str | None = None; authority: str | None = None; action_date: date | None = None; confidence_score: float = 0

