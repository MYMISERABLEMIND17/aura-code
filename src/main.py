from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from pathlib import Path
import uuid
from src.api.v1 import auth, ingest, aura, svg
from src.core.exceptions import AuraCodeException

app = FastAPI(title="AuraCode Engine", version="5.0.0")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    current_dir = Path(__file__).resolve().parent
    paths_to_check = [
        current_dir / "web" / "index.html",
        current_dir.parent / "api" / "index.html",
        Path("/var/task/src/web/index.html"),
        Path("/var/task/api/index.html"),
    ]
    for p in paths_to_check:
        if p.exists():
            return HTMLResponse(content=p.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>AuraCode Engine API</h1>")

@app.exception_handler(AuraCodeException)
async def auracode_exception_handler(request: Request, exc: AuraCodeException):
    correlation_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "correlation_id": correlation_id}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "correlation_id": correlation_id}
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(svg.router, prefix="/api/aura", tags=["svg"])
app.include_router(aura.router, prefix="/api/aura", tags=["aura"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

