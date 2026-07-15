# Installation Guide

First-time setup, from a fresh clone to a fully running application. For day-to-day development after this, see `LOCAL_DEVELOPMENT.md`.

## Prerequisites

- Python 3.12+ (backend uses modern type hint syntax — `str | None`, etc.)
- Node.js 18+ and npm
- No external database required — SQLite ships with Python

## 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python3 -m venv venv

# Install dependencies (note: --break-system-packages not needed inside a venv)
./venv/bin/pip install -r requirements.txt

# Copy the environment template
cp .env.example .env
```

Open `.env` and set `SECRET_KEY` to a real value:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output as `SECRET_KEY=...` in `.env`. This is optional for local development (the app falls back to a default and logs a warning) but **required** before any deployment — see `SECURITY.md`.

### Train the AI models

Arogent Verify's Behaviour Consistency signal and Arogent Risk's diabetes model both need to be trained once before the API can use them (they're loaded lazily on first request, not at import time):

```bash
./venv/bin/python -m app.ai.train_anomaly_model
./venv/bin/python -m app.ai.train_risk_model
```

Both scripts print their own validation metrics and save artifacts to `backend/app/ai/models/`. Re-run them any time `backend/app/ai/synthetic_data.py` changes.

### Start the backend

```bash
./venv/bin/uvicorn app.main:app --reload
```

Confirm it's running: `curl http://127.0.0.1:8000/health` should return `{"status":"healthy"}`. Interactive API docs (Swagger UI) are at `http://127.0.0.1:8000/docs`.

## 2. Frontend Setup

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Confirm it's running by opening `http://127.0.0.1:5173` — you should see the Arogent login screen.

**Important:** the backend's CORS configuration only allows `http://localhost:5173` and `http://127.0.0.1:5173` by default (see `backend/app/config.py`'s `cors_origins`). Running the frontend on a different port during local development will cause every API request to fail with a CORS error — this isn't a bug, it's the security boundary working as intended. Either run on port 5173, or add your port to `CORS_ORIGINS` in `backend/.env`.

## 3. Create Your First Users

The app has no seeded users out of the box. Register one of each role via the API directly (there's no admin UI for this yet):

```bash
BASE=http://127.0.0.1:8000/api/v1

curl -X POST $BASE/auth/register -H "Content-Type: application/json" -d '{
  "full_name": "Your Name", "username": "asha1", "password": "yourpassword",
  "role": "ASHA", "assigned_village": "Wadgaon"
}'

curl -X POST $BASE/auth/register -H "Content-Type: application/json" -d '{
  "full_name": "PHC Officer", "username": "phc1", "password": "yourpassword",
  "role": "PHC_OFFICER"
}'

curl -X POST $BASE/auth/register -H "Content-Type: application/json" -d '{
  "full_name": "District Officer", "username": "district1", "password": "yourpassword",
  "role": "DISTRICT_OFFICER"
}'
```

Then log in through the UI at `http://127.0.0.1:5173/login` with any of these.

**Note:** `POST /auth/register` is currently open to anyone — see `SECURITY.md` for why this needs to change before any real deployment.

## 4. Verify Everything Works

```bash
# Backend tests
cd backend && ./venv/bin/pytest tests/

# Frontend build + typecheck + lint
cd frontend && npm run build && npx tsc -p tsconfig.app.json --noEmit && npm run lint
```

All should complete with no errors. See `LOCAL_DEVELOPMENT.md` for the full day-to-day testing workflow.
