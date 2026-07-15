# Deployment Guide

**Honesty note, stated plainly per this phase's rules: nothing in this document has been deployed or verified against a live Vercel/Render environment.** The config files below (`frontend/vercel.json`, `backend/render.yaml`) are written correctly for their platforms based on documented conventions, and the local build/test commands they invoke have been verified locally — but the actual deploy-and-confirm-it-works step was not performed, because doing so would require accounts and credentials outside this environment. Treat this as a verified-locally, ready-to-deploy starting point, not a deployment that has been proven to work end-to-end on those platforms.

## Frontend — Vercel

Config: `frontend/vercel.json` (already created).

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

The `rewrites` rule is not optional — without it, refreshing the browser on any client-side route (e.g. `/dashboard`) would 404, since Vercel would look for a literal file at that path instead of serving `index.html` and letting React Router handle it.

**Steps:**
1. Push the repo to GitHub (or connect Vercel directly to your Git provider)
2. Import the project in Vercel, set the root directory to `frontend/`
3. Set the environment variable `VITE_API_BASE_URL` to your deployed backend's URL (see below) — **must** include the `/api/v1` suffix
4. Deploy

## Backend — Render

Config: `backend/render.yaml` (already created).

```yaml
services:
  - type: web
    name: arogent-backend
    runtime: python
    plan: free
    buildCommand: >
      pip install -r requirements.txt &&
      python -m app.ai.train_anomaly_model &&
      python -m app.ai.train_risk_model
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        sync: false
      - key: CORS_ORIGINS
        sync: false
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "720"
    healthCheckPath: /health
```

**Why training runs in `buildCommand`:** both AI models are lazy-loaded on first request (`app/verify/anomaly.py`, `app/risk/model.py`) — if the `.joblib` files don't exist at all, the first real request would fail with a `RuntimeError`. Running the training scripts during build guarantees the models exist before the service starts serving traffic.

**`generateValue: true` for `SECRET_KEY`:** Render generates a random secure value automatically — this is the correct behavior and means you don't need to generate one yourself for a Render deployment specifically (the manual `secrets.token_hex(32)` approach in `INSTALLATION.md` is for local/other-platform deployment).

**Steps:**
1. Connect your GitHub repo to Render, or use `render.yaml`'s Blueprint feature to auto-configure from this file
2. Set `DATABASE_URL` and `CORS_ORIGINS` manually in Render's dashboard (marked `sync: false` above since they're deployment-specific, not safe to hardcode in a committed file)
3. `CORS_ORIGINS` must be a JSON array string containing your Vercel frontend's exact URL, e.g. `["https://arogent.vercel.app"]`

## Database — Production Migration Notes

**SQLite is not viable beyond a demo on most platforms, including Render's free tier**, whose filesystem is not guaranteed persistent across deploys/restarts — every redeploy could silently wipe all patient/screening data. This is a real constraint, not a hypothetical one.

**Migration path (notes only — not implemented in this codebase):**
1. Provision a managed Postgres instance (Render offers one directly; alternatively Supabase, Railway, or Neon)
2. Add `psycopg2-binary` (or `asyncpg` for an async setup) to `requirements.txt` — **not currently a dependency**, since the codebase has only been run against SQLite
3. Set `DATABASE_URL` to the Postgres connection string, e.g. `postgresql://user:pass@host:5432/arogent`
4. No SQLAlchemy model code needs to change — the codebase deliberately avoids SQLite-specific syntax throughout (see `app/database.py`'s docstring), so this should be a connection-string-only change, but this claim has **not been tested against a real Postgres instance** in this project and should be verified before trusting it in production
5. Table creation currently happens via `Base.metadata.create_all()` in `app/main.py`'s lifespan handler — fine for a demo, but a real production setup should introduce Alembic migrations instead, so schema changes don't require a full table recreation. **Not implemented** — noted as a gap, not built.

## Pre-Deployment Checklist

Cross-referencing `SECURITY.md` and `ENVIRONMENT_VARIABLES.md` — do not deploy without:

- [ ] `SECRET_KEY` set to a real generated value (or Render's `generateValue: true`)
- [ ] `CORS_ORIGINS` set to the actual deployed frontend URL
- [ ] `VITE_API_BASE_URL` set to the actual deployed backend URL
- [ ] Decide what to do about `POST /auth/register` being open to the public (see `SECURITY.md`) — as shipped, anyone can self-register as `DISTRICT_OFFICER`
- [ ] Migrate off SQLite if data persistence matters (see above)
- [ ] Accept that there's no rate limiting on `/auth/login` (see `SECURITY.md`) — a public deployment is exposed to brute-force attempts with no protection
