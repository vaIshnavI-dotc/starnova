# Step-by-step execution plan

## Phase 1 — Run the backend skeleton
1. Install Python 3.11+.
2. Open this backend folder in VS Code (not the old Express folder).
3. Run `py -m venv .venv`.
4. Activate with `.venv\\Scripts\\Activate.ps1`.
5. Install dependencies: `python -m pip install -r requirements.txt`.
6. Copy `.env.example` to `.env`.
7. Run `uvicorn app.main:app --reload --port 8000`.
8. Visit `/`, `/api/v1/meta`, and `/docs`.

## Phase 2 — Validate API contract
In Swagger `/docs`, check that all 11 endpoints appear under `/api/v1`. Test the GET routes; empty data is expected until ingestion is implemented. Try invalid POST bodies for `/analyze` and `/eval` to verify 422 errors.

## Phase 3 — Create fixture data
Create a small, clearly synthetic fixture dataset. Populate sources, tips, scored_tips, source_stats, coordination tables, and archive_chain. Confirm every returned record has `data_origin`.

## Phase 4 — Build modules in ownership order
- P1: ingestion pipeline, `/meta`, SHA-256 tip hashes, archive chain and verification.
- P2: extraction schema and live `/analyze`; cached fallback when extractor unavailable.
- P3: scoring, benchmark excess returns, beta-binomial source stats, source leaderboard/profile, coordination flags and graph.
- P4: evaluation sessions, decisions, aggregate metrics, frontend integration.

## Phase 5 — Test and freeze
- Validate response shapes against F3_API_Contract.docx examples.
- Test pagination/sorting/filtering.
- Test unknown IDs -> 404 `not_found`.
- Test malformed bodies -> 422 `validation_error`.
- Test no ticker -> 422 `unparseable_tip`.
- Test extractor unavailable -> 503 `extractor_unavailable` and frontend cached fallback.
- Confirm no endpoint emits recommendations, buy/sell signals, or position suggestions.
- Freeze schemas and generate frontend types from `/openapi.json`.
