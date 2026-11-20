from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, FRONTEND_ORIGIN
from app.core.database import init_db
from app.api.routes import router as api_router

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="Tip Checkpoint API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


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


app.include_router(api_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}