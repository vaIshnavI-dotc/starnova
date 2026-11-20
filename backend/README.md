# Tip Checkpoint (Signal / Noise) — Backend API

An extended, production-grade FastAPI + SQLite backend for **Tip Checkpoint** (`Signal / Noise`). The backend provides a rigorous decision-gate checkpoint for retail stock tips, enforcing thesis auditing, link verification with real market data, fixed sector and core questioning templates, investment confirmations, and Bayesian source tracking.

## Core Principles
1. **No Price Predictions / No Buy-Sell Signals**: The app never predicts prices or says buy or sell.
2. **Backend Decision Gate**: The backend (not the LLM) decides what gets recorded, whether a decision gate has passed, and validates all parameters.
3. **Safe Migrations & Contract Invariance**: Fixed API contract (`API_CONTRACT.md`), backwards-compatible schema migrations, consistent error shapes.

---

## Quick Setup

### 1. Prerequisites
- Python 3.11+
- Virtual environment (PowerShell on Windows):
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Key settings in `.env`:
```env
APP_NAME="Tip Checkpoint API"
DB_PATH="app/data/tip_checkpoint.db"
FRONTEND_ORIGINS="http://localhost:5173,http://localhost:3000"
JWT_SECRET="signalnoise-hackathon-supersecret-jwt-key-2026"
LLM_PROVIDER="gemini"
LLM_API_KEY=""
LLM_MODE="mock"   # "mock" for deterministic offline demo, "gemini" for live LLM
```

### 4. Run Server
```powershell
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Base API URL: `http://localhost:8000/api/v1`

---

## Seed Data & Demo User
On startup, idempotent migrations and seed data are automatically loaded:
- **Demo User**: `demo@signalnoise.app` / `demo1234`
- **Personal Sources**:
  - `Neel` (4 tips, 1 worked, `shrunk_hit_rate`: 0.31, label: `"Too early to tell"`)
  - `Kushal` (3 tips, 2 worked, `shrunk_hit_rate`: 0.55, label: `"Too early to tell"`)
  - `Anonymous tip` (5 tips, 1 worked, `shrunk_hit_rate`: 0.27, label: `"Too early to tell"`)
- **Past Decisions**: Includes 4 buys after an 8%+ jump, 3 of which lost money (powering user insights).
- **Alerts**: 3 alerts of types `outcome_confirmed`, `negative_outcome`, and `new_update`.

---

## Testing
Run the complete test suite with `pytest`:
```powershell
python -m pytest -v tests/test_api.py
```
Tests cover:
- Gate validation (`POST /decisions/lock` with missing fields -> `422 gate_incomplete`)
- One-question-per-turn rule (single question text block + `__dont_know__` reply)
- 6-question cap (transition to `gate` stage after 6 questions)
- No `thesis_chain` returned before thesis submission
- `investment_confirm` draft created only on completed purchase statements with all 4 fields
- Alerts endpoints (`GET /alerts`, `POST /alerts/{id}/read`, `POST /alerts/read_all`)
- Insights endpoint (`GET /insights`)
- Automated and manual scoring job execution (`run_scoring_job`)
- Preservation of all pre-existing endpoints

---

## API Summary (`/api/v1`)

| Endpoint | Method | Description |
|---|---|---|
| `/auth/signup` | POST | Register new user `{name, email, password}` -> `{token, user}` |
| `/auth/login` | POST | Login `{email, password}` -> `{token, user}` |
| `/auth/me` | GET | Current authenticated user `{user}` |
| `/chat/message` | POST | Multipart chat state machine (intake, thesis, questions, gate) |
| `/conversations/{id}` | GET | Retrieve conversation messages and block history |
| `/decisions/lock` | POST | Validates and locks trade decision (`422 gate_incomplete` on missing fields) |
| `/decisions` | GET | List user decisions with stock & source metadata |
| `/investments/confirm` | POST | Confirms investment draft using 30-min token |
| `/investments` | GET | List user holdings with live current value |
| `/insights` | GET | Behavioral pattern analysis (e.g. 8%+ jump loss rate) |
| `/alerts` | GET | List alerts with 7d/30d/90d horizon results |
| `/alerts/{id}/read` | POST | Mark alert as read |
| `/alerts/read_all` | POST | Mark all alerts as read |
| `/sources` | GET | Extended profile source stats with shrinkage and evidence levels |
| Pre-existing | GET/POST | `/meta`, `/sources/{id}`, `/tips/{id}`, `/coordination/*`, `/archive/*`, `/analyze`, `/eval/*` |
