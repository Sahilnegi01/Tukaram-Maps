import enum
import uuid
from datetime import datetime, timezone
from geoalchemy2 import Geography
from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Index, String, Table, Text, UniqueConstraint, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.domain.enums import ActionStatus, ActionType, CurrentStatus, EstablishmentType, ReviewStatus, SourceType

def utcnow(): return datetime.now(timezone.utc)
class Base(DeclarativeBase): pass
class ProcessingStatus(str, enum.Enum):
    NEW="NEW"; PROCESSING="PROCESSING"; PROCESSED="PROCESSED"; REJECTED="REJECTED"; ERROR="ERROR"

action_articles = Table("action_articles", Base.metadata,
    Column("action_id", UUID(as_uuid=True), ForeignKey("actions.id", ondelete="CASCADE"), primary_key=True),
    Column("article_id", UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True))

class EstablishmentModel(Base):
    __tablename__ = "establishments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300)); normalized_name: Mapped[str] = mapped_column(String(300), index=True)
    type: Mapped[EstablishmentType] = mapped_column(Enum(EstablishmentType, name="establishment_type"), index=True)
    address: Mapped[str | None] = mapped_column(Text); city: Mapped[str] = mapped_column(String(120), index=True); state: Mapped[str] = mapped_column(String(120), index=True)
    district: Mapped[str | None] = mapped_column(String(120)); pincode: Mapped[str | None] = mapped_column(String(10))
    latitude: Mapped[float | None] = mapped_column(Float); longitude: Mapped[float | None] = mapped_column(Float)
    location: Mapped[object | None] = mapped_column(Geography("POINT", srid=4326))
    current_status: Mapped[CurrentStatus] = mapped_column(Enum(CurrentStatus, name="current_status"), index=True, default=CurrentStatus.UNKNOWN)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    actions = relationship("ActionModel", back_populates="establishment", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_establishments_location", "location", postgresql_using="gist"),)

class ActionModel(Base):
    __tablename__ = "actions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    establishment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("establishments.id", ondelete="CASCADE"), index=True)
    action_type: Mapped[ActionType] = mapped_column(Enum(ActionType, name="action_type"), index=True)
    reason: Mapped[str | None] = mapped_column(Text); authority: Mapped[str | None] = mapped_column(String(300)); action_date: Mapped[object | None] = mapped_column(Date, index=True)
    status: Mapped[ActionStatus] = mapped_column(Enum(ActionStatus, name="action_status"), index=True, default=ActionStatus.PENDING_REVIEW)
    confidence_score: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    establishment = relationship("EstablishmentModel", back_populates="actions"); articles = relationship("ArticleModel", secondary=action_articles, back_populates="actions")
    reviews = relationship("ReviewRequestModel", back_populates="action")

class SourceModel(Base):
    __tablename__ = "sources"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200)); domain: Mapped[str] = mapped_column(String(200)); source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type"))
    feed_url: Mapped[str | None] = mapped_column(Text); city: Mapped[str | None] = mapped_column(String(120)); state: Mapped[str | None] = mapped_column(String(120)); enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_successful_fetch: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); last_failed_fetch: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); last_error: Mapped[str | None] = mapped_column(Text); consecutive_failures: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    articles = relationship("ArticleModel", back_populates="source")
    __table_args__ = (UniqueConstraint("domain", "feed_url", name="uq_source_feed"),)

class ArticleModel(Base):
    __tablename__ = "articles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), index=True); title: Mapped[str] = mapped_column(String(600)); normalized_title: Mapped[str] = mapped_column(String(600), index=True)
    url: Mapped[str] = mapped_column(Text); canonical_url: Mapped[str] = mapped_column(Text, unique=True); url_hash: Mapped[str] = mapped_column(String(64), unique=True)
    content: Mapped[str | None] = mapped_column(Text); summary: Mapped[str | None] = mapped_column(Text); published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True)); fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True); processing_status: Mapped[ProcessingStatus] = mapped_column(Enum(ProcessingStatus, name="processing_status"), default=ProcessingStatus.NEW, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow); updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    source = relationship("SourceModel", back_populates="articles"); actions = relationship("ActionModel", secondary=action_articles, back_populates="articles")

class ReviewRequestModel(Base):
    __tablename__ = "review_requests"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("actions.id", ondelete="CASCADE"), index=True); token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus, name="review_status"), default=ReviewStatus.PENDING, index=True); expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow); reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    action = relationship("ActionModel", back_populates="reviews")

