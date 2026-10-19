import base64
import hmac
import hashlib
import json
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.config import settings

sec_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(sec_scheme)) -> dict:
    try:
        parts = credentials.credentials.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        header_b64, payload_b64, sig_b64 = parts
        message = f"{header_b64}.{payload_b64}"
        expected_sig_bytes = hmac.new(settings.JWT_SECRET.encode(), message.encode(), hashlib.sha256).digest()
        expected_sig = base64.urlsafe_b64encode(expected_sig_bytes).rstrip(b"=")
        
        sig_b64_padded = sig_b64 + "=" * (-len(sig_b64) % 4)
        actual_sig = base64.urlsafe_b64decode(sig_b64_padded)
        
        if not hmac.compare_digest(base64.urlsafe_b64decode(expected_sig + b"=" * (-len(expected_sig) % 4)), actual_sig):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
            
        payload_padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_padded).decode())
        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
