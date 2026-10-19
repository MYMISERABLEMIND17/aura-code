from sqlalchemy import Column, String, Integer, BigInteger, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(39), unique=True, nullable=False)
    avatar_url = Column(Text, nullable=False)
    aura_score = Column(Integer, nullable=False, default=0)
    archetype = Column(String(64), nullable=False, default="The 3 AM Cowboy")
    roast_commentary = Column(Text, nullable=False, default="Pending analysis")
    version_hash = Column(String(32), nullable=False, default="v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
