from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, FRONTEND_ORIGINS
from app.core.database import init_db
from app.core.migrations import run_migrations
from app.core.seed import seed_demo_data
from app.services.scoring import start_scoring_scheduler
from app.api.routes import router as api_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.decisions import router as decisions_router
from app.api.investments import router as investments_router
from app.api.insights import router as insights_router
from app.api.alerts import router as alerts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    run_migrations()
    seed_demo_data()
    try:
        start_scoring_scheduler()
    except Exception:
        pass
    yield


app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="Tip Checkpoint API",
    lifespan=lifespan
)

# CORS per contract: http://localhost:5173 and http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error shape handler per contract: {"error": {"code": "...", "message": "...", "details": {...}}}
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    code = "server_error"
    if exc.status_code == 401:
        code = "unauthorized"
    elif exc.status_code == 404:
        code = "not_found"
    elif exc.status_code == 422:
        code = "validation_error"

    message = "An error occurred"
    details = {}

    if isinstance(exc.detail, dict):
        code = exc.detail.get("code") or exc.detail.get("error") or code
        message = exc.detail.get("message") or str(exc.detail)
        details = exc.detail.get("details", {})
        if not details:
            details = {k: v for k, v in exc.detail.items() if k not in ("code", "error", "message")}
    elif isinstance(exc.detail, str):
        message = exc.detail

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()}
            }
        }
    )


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Tip Checkpoint API is running",
        "docs": "/docs"
    }


@app.get("/api/v1/meta")
def get_meta():
    return {
        "success": True,
        "app": APP_NAME,
        "version": "1.0.0"
    }


# Include routers under /api/v1 as specified by contract
app.include_router(api_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(decisions_router, prefix="/api/v1")
app.include_router(investments_router, prefix="/api/v1")
app.include_router(insights_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")

# Also include at root for direct path matching convenience
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(decisions_router)
app.include_router(investments_router)
app.include_router(insights_router)
app.include_router(alerts_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
