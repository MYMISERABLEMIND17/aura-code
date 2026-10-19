import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/auracode")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    SQS_FETCHER_URL: str = os.getenv("SQS_FETCHER_URL", "http://localhost:4566/queue/auracode-fetcher")
    SQS_CALCULATOR_URL: str = os.getenv("SQS_CALCULATOR_URL", "http://localhost:4566/queue/auracode-calculator")
    SQS_PERSIST_URL: str = os.getenv("SQS_PERSIST_URL", "http://localhost:4566/queue/auracode-persist")
    SQS_PURGE_URL: str = os.getenv("SQS_PURGE_URL", "http://localhost:4566/queue/auracode-purge")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")

settings = Settings()

