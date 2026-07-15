# Local Development Guide

Assumes you've already completed `INSTALLATION.md`.

## Daily Workflow

```bash
# Terminal 1 — backend
cd backend && ./venv/bin/uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

Both support hot reload — backend on any `.py` change, frontend on any `.ts`/`.tsx` change.

## Running Tests

### Backend (93 tests across 3 suites)

```bash
cd backend
./venv/bin/pytest tests/                    # everything
./venv/bin/pytest tests/verify/ -v          # Arogent Verify only (57 tests)
./venv/bin/pytest tests/risk/ -v            # Arogent Risk only (16 tests)
./venv/bin/pytest tests/api/ -v             # API/integration only (20 tests)
```

### Frontend

```bash
cd frontend
npm run build                                        # tsc -b && vite build
npx tsc -p tsconfig.app.json --noEmit                 # standalone strict typecheck
npm run lint                                          # oxlint
```

There is no frontend unit test runner (Vitest/RTL) configured — frontend correctness has been verified throughout via strict TypeScript, ESLint/oxlint, and real-browser Playwright integration tests against a running backend (see below), not component-level unit tests. This is a deliberate scope decision for the hackathon timeline, not an oversight — noted here rather than left implicit.

## Full-Stack Integration Testing

The project has been verified via Playwright driving a real Chromium browser against both a real running backend and frontend — not mocked. This isn't part of an automated CI suite (no CI is configured), but the pattern below is how every module was verified during development:

```bash
# Terminal 1
cd backend && ./venv/bin/uvicorn app.main:app --port 8000 --host 127.0.0.1

# Terminal 2
cd frontend && npm run dev -- --port 5173 --host 127.0.0.1

# Then drive a browser against http://127.0.0.1:5173 with Playwright/Selenium/manual testing
```

**Gotcha:** if you're scripting this, don't rely on fixed `sleep` delays for "is the server ready yet" — poll `/health` instead. Also don't use browser-navigation waits (`wait_for_url`) for React Router's client-side routing; it never fires a real page-load event. Wait for content instead (`wait_for_selector`).

## Seeding Test Data

There's no seed script — the fastest way to get realistic data is to register users via `curl` (see `INSTALLATION.md`) and then submit real screenings through the UI or API. For district dashboard testing, seed screenings across a few different villages and outcomes (implausible glucose for `NEEDS_REVIEW`, high glucose + family history + low activity for `HIGH` risk) to see the charts populated meaningfully.

## Resetting the Database

```bash
cd backend
rm -f arogent.db
```

The next server start recreates all tables (via `Base.metadata.create_all()` in `app/main.py`'s lifespan handler) but does not reseed any data.

## Retraining the AI Models

If you change `backend/app/ai/synthetic_data.py` (the synthetic data generator), both models need retraining:

```bash
./venv/bin/python -m app.ai.train_anomaly_model
./venv/bin/python -m app.ai.train_risk_model
```

`train_risk_model.py` prints which model was chosen (Logistic Regression vs XGBoost) and why — it automatically prefers the more interpretable Logistic Regression unless XGBoost beats it by a meaningful margin (see the script's `XGBOOST_IMPROVEMENT_THRESHOLD`).

## Known Environment Gotchas (learned the hard way during development)

- **CORS is port-specific.** The backend only allows origins `http://localhost:5173` and `http://127.0.0.1:5173` by default. Running the frontend dev server on any other port will fail every API call with a CORS error that looks like a bug but isn't.
- **`bcrypt` version matters.** `passlib==1.7.4`'s own internal self-check breaks with `bcrypt>=4.1`. `requirements.txt` pins `bcrypt==4.0.1` for exactly this reason — don't let it drift.
- **SQLite `:memory:` + multi-threaded test clients need `StaticPool`.** If you write a new test using FastAPI's `TestClient` against an in-memory SQLite DB, you need `poolclass=StaticPool` in the test engine — otherwise different threads get different, empty in-memory databases. See `tests/api/conftest.py` for the working pattern.
