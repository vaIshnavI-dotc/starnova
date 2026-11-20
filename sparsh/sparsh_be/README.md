# Tip Checkpoint — API Contract Backend Skeleton

This backend skeleton follows the attached **F3 API Contract v1.0**: Python/FastAPI, SQLite, Pydantic-style request validation, JSON responses, `/api/v1`, no authentication in hackathon scope, and CORS for the frontend origin. It is intentionally not a MongoDB/Express CRUD project.

## Setup (Windows PowerShell)
1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Create environment: `py -m venv .venv`
4. Activate: `.venv\\Scripts\\Activate.ps1` (if script execution is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` then activate again).
5. Install: `python -m pip install -r requirements.txt`
6. Copy `.env.example` to `.env`.
7. Run: `uvicorn app.main:app --reload --port 8000`
8. Swagger: http://localhost:8000/docs

## Routes currently scaffolded
- GET `/api/v1/meta`
- POST `/api/v1/analyze` (cached match if ticker exists; otherwise 503 until live extractor is added)
- GET `/api/v1/sources` (paginated; sorting/filtering)
- GET `/api/v1/sources/{source_id}`
- GET `/api/v1/tips/{tip_id}`
- GET `/api/v1/coordination/flags`
- GET `/api/v1/coordination/graph?ticker=ABC`
- GET `/api/v1/archive/verify/{tip_id}`
- GET `/api/v1/archive/chain/head`
- POST `/api/v1/eval/sessions`
- POST `/api/v1/eval/decisions`
- GET `/api/v1/eval/results`

## Important status
This is a runnable skeleton, not the finished pipeline. Tables are initialized automatically. With no data loaded, list endpoints return empty results. Extraction, analytics, archive recomputation, and evaluation statistics still need their full implementations. The `/analyze` route has a regex ticker placeholder and cached lookup only; replace it with the LLM/rules extractor and matching service.

## Contract constraints
- No buy/sell recommendation or action fields.
- All records should carry `data_origin` (`real` or `synthetic`).
- Timestamp convention is UTC ISO-8601.
- Cost model and assumptions should be exposed by `/meta` and kept explicit.
- Schemas should be frozen; later changes should be additive or moved to `/v2`.
