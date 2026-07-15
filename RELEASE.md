# Release Notes — v1.0.0 (MVP)

## What's Included

The full pipeline is implemented and verified end-to-end: **Login → Register Patient → Screening → Arogent Verify → Arogent Risk (if eligible) → Referral → Result Screen → District Dashboard.**

- **Backend**: FastAPI + SQLAlchemy, 93 automated tests (unit, integration, and full API/RBAC coverage)
- **Frontend**: React 19 + TypeScript (strict mode), 5 screens, verified via real-browser Playwright integration tests against a running backend at every development stage
- **AI**: Arogent Verify (confidence scoring, 4 independent signals) and Arogent Risk (diabetes prediction), both trained on synthetic data with an explicit disclosure — see `README.md`

## Deployment Status

**Not deployed.** This release has been fully verified locally (backend tests, frontend build/typecheck/lint, and full-stack Playwright integration tests) but has **not** been deployed to a live, publicly accessible environment from this development process. Deployment configuration is prepared and ready (`frontend/vercel.json`, `backend/render.yaml`, `docs/DEPLOYMENT.md`), but the actual deploy-and-verify-live step requires manual action — see `docs/DEPLOYMENT.md` for exact steps.

## Known Limitations (see `docs/SECURITY.md` and `README.md` for full detail)

- `POST /auth/register` is currently public — anyone can self-register as any role, including `DISTRICT_OFFICER`. **Must be addressed before any real deployment.**
- No row-level data scoping — any authenticated user can view any patient/screening/referral, not just ones relevant to their own assignment.
- No token revocation mechanism — a compromised JWT remains valid until its natural 12-hour expiry.
- No rate limiting on any endpoint, including login.
- SQLite is used throughout; not suitable for production persistence on most hosting platforms (ephemeral filesystems) — see `docs/DEPLOYMENT.md`'s migration notes.
- "Recent Screenings" on the District Dashboard is an honest placeholder — no backend endpoint exists yet for a district-wide recent-screenings list.
- Diabetes screening only — anaemia, hypertension, and TB pathways from the original proposal are not built.

## Before You Deploy This Publicly

Read `docs/SECURITY.md` and `docs/DEPLOYMENT.md`'s pre-deployment checklist in full. At minimum: set a real `SECRET_KEY`, set `CORS_ORIGINS` to your actual deployed frontend URL, set `VITE_API_BASE_URL` to your actual deployed backend URL, and make a deliberate decision about the open registration endpoint.

## Data Disclosure

All AI components are trained on synthetic data (`backend/app/ai/synthetic_data.py`). No real patient, ASHA, or government health data is used anywhere in this project. This is a decision-support tool, not a diagnostic one — a clinician always makes the final call.
