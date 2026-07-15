# Changelog

All notable changes to this project are documented here, grouped by the module/phase they were built in. Format loosely follows Keep a Changelog (keepachangelog.com).

## [1.0.0] — MVP Complete

### Phase 11 — Git Repository Finalization
- Removed 4 unused default-template assets (hero.png, react.svg, vite.svg, icons.svg) — confirmed zero references before removal, rebuild verified identical output
- Excluded generated ML model artifacts (backend/app/ai/models/) from version control — reproducible via documented training scripts, not meant to be committed
- Added LICENSE (MIT, with a clarifying note that it doesn't imply medical device certification)
- Added RELEASE.md, this CHANGELOG.md

### Phase 10 — Final Polish, Deployment Prep, Documentation
- Fixed 9 unused imports, 6 missing exception chains (raise ... from e), 1 unsafe zip() call (backend, via ruff)
- Added backend/.env.example, frontend/.env.example (neither existed before)
- Fixed a real gap: frontend's API base URL was hardcoded to 127.0.0.1:8000 with no environment variable at all — moved to VITE_API_BASE_URL
- Added missing frontend/src/vite-env.d.ts (should have shipped from the Module 1 Vite template)
- Lazy-loaded the District Dashboard route (React.lazy + Suspense) — measured 865.29 kB -> 482.39 kB main bundle (44% reduction), Dashboard split into its own 382.90 kB chunk
- Added basic logging configuration and a startup warning if the default (insecure) SECRET_KEY is still in use
- Full security review — see docs/SECURITY.md for findings (two real gaps flagged, not fixed: public registration endpoint, no row-level data scoping)
- Created 8 documentation files under docs/ plus deployment config (frontend/vercel.json, backend/render.yaml)

### Module 9 — District Dashboard
- Confidence Distribution, Diabetes Risk Distribution, Referral Status, and Village Hotspot charts (Recharts), backed entirely by the existing GET /dashboard and GET /referrals endpoints — no new backend logic
- MetricCard-based top metrics row, reusing the Module 6 component rather than duplicating it
- Honestly labeled placeholder for "Recent Screenings" — no backend endpoint exists for a district-wide recent-screenings list

### Module 8 — Screening Form & Result Screen
- Full diabetes screening form with patient search, clinical inputs, optional height/weight -> BMI helper, optional GPS capture
- Result screen: recommendation banner, Screening Confidence + Confidence Fingerprint (four-signal breakdown), Diabetes Risk (shown only when confidence is HIGH), referral status

### Module 7 — Authentication & Patient Registration
- JWT login/logout with localStorage persistence, session restore on reload, auto-logout at token expiry
- Role-based route protection (ProtectedRoute)
- Patient registration form (fields matching the backend PatientCreate schema exactly)

### Module 6 — Frontend Design System
- Healthcare-appropriate design tokens (medical blue / success / warning / danger / neutral), Lexend/Inter/IBM Plex Mono type system
- ConfidenceFingerprint — the project's signature visual element, making Arogent Verify's four-signal mechanism visible rather than showing a single opaque number
- 15 reusable components (AppShell, Card, badges, states, etc.)

### Module 5 — Backend API
- Full REST API: auth, patients, screenings, referrals, dashboard
- Role-based access control (require_roles()) enforced per-endpoint
- Explicit Referral model/engine (not just a status flag)
- 20 API-level tests via TestClient

### Module 4 — Arogent Risk
- Diabetes risk model: Logistic Regression vs. XGBoost compared on validation AUC, more interpretable model preferred unless XGBoost wins by a meaningful margin
- Confidence gate enforced structurally (ConfidenceGateError) — Arogent Risk cannot run on non-HIGH-confidence data, by construction, not convention
- Per-prediction feature contributions (not just global importance)

### Module 3 — Arogent Verify
- Four independent consistency signals (Clinical, Historical, Behaviour, Geographic) combined via a documented, deterministic weighted average
- Proportional reweighting when a signal is genuinely unavailable (e.g. a patient's first screening) — missing data is never treated as suspicious
- Fully deterministic scoring and explanation generation — no LLM in the scoring path

### Module 2 — Database Models
- SQLAlchemy models: User, Patient, Screening, Referral
- Shared enums (ConfidenceStatus, RiskLevel, ReferralStatus, UserRole) instead of hardcoded strings

### Module 1 — Project Scaffolding
- FastAPI + SQLAlchemy + SQLite backend; React 19 + Vite + TypeScript + Tailwind frontend
