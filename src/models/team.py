from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from src.models.user import Base

class TeamInstallation(Base):
    __tablename__ = "team_installations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(BigInteger, unique=True, nullable=False)
    github_install_id = Column(BigInteger, unique=True, nullable=False)
    installed_at = Column(DateTime(timezone=True), server_default=func.now())
