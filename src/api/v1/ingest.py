from fastapi import APIRouter, Depends, status
import uuid
from src.core.security import verify_token

router = APIRouter()

@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_ingestion(payload: dict, token: dict = Depends(verify_token)):
    job_id = str(uuid.uuid4())
    return {"status": "queued", "job_id": job_id, "estimated_seconds": 6}
