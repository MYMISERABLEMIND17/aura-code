from sqlalchemy import Column, Numeric, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from src.models.user import Base

class MetricsSnapshot(Base):
    __tablename__ = "metrics_snapshots"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    churn_ratio = Column(Numeric(5, 4), nullable=False, default=0.0)
    weekend_commit_ratio = Column(Numeric(3, 2), nullable=False, default=0.0)
    pr_turnaround_hours = Column(Numeric(8, 2), default=0.0)
    review_latency_hours = Column(Numeric(8, 2), default=0.0)
    workflow_type = Column(String(32), nullable=False, default="Standard")
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        {"postgresql_partition_by": "HASH (user_id)"}
    )
