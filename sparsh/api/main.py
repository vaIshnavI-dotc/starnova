"""FastAPI application entry point."""
from fastapi import FastAPI
from api.routers import meta, archive

app = FastAPI(title="Sparsh API", version="0.1.0")
app.include_router(meta.router)
app.include_router(archive.router)
