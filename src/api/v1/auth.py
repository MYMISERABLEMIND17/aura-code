from fastapi import APIRouter
import base64
import hmac
import hashlib
import json
from src.core.config import settings

router = APIRouter()

@router.post("/token")
async def get_token(username: str):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"sub": username}).encode()).rstrip(b"=").decode()
    message = f"{header}.{payload}"
    signature = base64.urlsafe_b64encode(
        hmac.new(settings.JWT_SECRET.encode(), message.encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    token = f"{message}.{signature}"
    return {"access_token": token, "token_type": "bearer"}
