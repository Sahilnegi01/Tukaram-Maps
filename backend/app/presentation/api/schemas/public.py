from datetime import date
from pydantic import BaseModel, Field, model_validator
from app.domain.enums import ActionType, CurrentStatus, EstablishmentType
class MapParams(BaseModel):
    north: float | None=None; south: float | None=None; east: float | None=None; west: float | None=None
    zoom: int = Field(default=5, ge=1, le=20); state: str | None=None; city: str | None=None; type: EstablishmentType | None=None; current_status: CurrentStatus | None=None; action_type: ActionType | None=None; from_date: date | None=None; to_date: date | None=None
    @model_validator(mode="after")
    def bounds(self):
        supplied=[self.north,self.south,self.east,self.west]
        if any(v is not None for v in supplied) and any(v is None for v in supplied): raise ValueError("All viewport bounds are required together")
        if self.north is not None and (self.north <= self.south or not -90 <= self.south <= 90 or not -90 <= self.north <= 90 or not -180 <= self.west <= 180 or not -180 <= self.east <= 180): raise ValueError("Invalid viewport bounds")
        return self
