# Project Architecture

## System Overview

```
Frontend (React)
      |
      v
FastAPI Routes  --  thin: no scoring/thresholds/gating logic here
      |
      v
Pipeline Orchestrator (app/pipeline)
      |
      +----------> Arogent Verify (app/verify)
      |                   |
      |             confidence == HIGH?
      |                   |
      |             Yes --+--> Arogent Risk (app/risk)
      |                              |
      |                        risk_level == HIGH?
      |                              |
      |                        Yes --+--> Referral Engine (app/referral)
      |
      +----------> Database (SQLAlchemy / SQLite)
```

`app/verify`, `app/risk`, and `app/referral` do not import each other. Neither `app/verify` nor `app/risk` knows the other exists — `app/pipeline/service.py` is the *only* place that composes them. This is deliberate: it means each package is independently unit-testable (see `tests/verify/` and `tests/risk/`, neither of which imports the pipeline), and it means the "Risk never runs on low-confidence data" claim is a structural fact about the codebase, not a convention someone has to remember to follow correctly.

## The Confidence Gate — Enforced Twice

1. **Inside `app/risk/service.py`**: `predict_diabetes_risk()` raises `ConfidenceGateError` if called with anything but `ConfidenceStatus.HIGH`. This makes it structurally impossible to call Arogent Risk on non-HIGH data by accident — the check lives inside the function itself, not in the caller's discipline.
2. **In the Pipeline Orchestrator**: `run_screening_pipeline()` only calls Arogent Risk at all if `screening.confidence_status == ConfidenceStatus.HIGH`. A caller that skipped this check would still be caught by layer 1.

## Arogent Verify — Four Consistency Signals

Rather than a single confidence number pulled from nowhere, Arogent Verify computes four independent signals and combines them with a documented, deterministic weighted average:

| Signal | Weight | What it checks |
|---|---|---|
| Clinical Consistency | 35% | Hard physiological bounds + whether glucose/BMI/symptoms/family history cohere |
| Historical Consistency | 30% | Implausible swings vs. the patient's own prior screenings; duplicate-screening detection |
| Behaviour Consistency | 20% | Deterministic workflow metrics (screening pace, working hours) blended with an Isolation Forest anomaly score |
| Geographic Consistency | 15% | Village-name match + optional GPS distance from the assigned service region |

**Missing-data principle:** a signal that's genuinely unavailable (e.g. a patient's first-ever screening has no history to compare against) is excluded from the weighted average and the remaining weights are proportionally renormalized — missing information is never treated as suspicious. See `app/verify/aggregate.py`.

**Deterministic by design:** confidence scoring is fully deterministic and reproducible from the same inputs. No generative AI participates in scoring — `app/verify/explain.py`'s explanation bullets are template-based, not LLM-generated, specifically so the same inputs always produce the same score and the same explanation.

Full technical detail: read `app/verify/service.py`'s docstring and each signal module's own docstring (`rules.py`, `historical.py`, `anomaly.py`, `geographic.py`).

## Arogent Risk — Model Selection

Trained via `app/ai/train_risk_model.py`: Logistic Regression and XGBoost are both trained on the same synthetic data and compared on a held-out validation split. XGBoost is only deployed if it beats Logistic Regression by >=0.02 AUC — otherwise the more interpretable Logistic Regression is used, since a healthcare decision-support tool benefits more from per-prediction explainability (real coefficient x value contributions, computed in `app/risk/features.py`) than from a small accuracy gain.

## Data Model

```
User (ASHA / PHC_OFFICER / DISTRICT_OFFICER)
  |
  +-- registers --> Patient
                       |
                       +-- has many --> Screening
                                           |
                                           +-- may generate --> Referral
```

Every `Screening` row stores the raw clinical inputs, all four Arogent Verify sub-scores individually (not just the final number — auditability), the confidence status/score, and (only if applicable) the risk score/level and referral status.

## Frontend Architecture

```
main.tsx: BrowserRouter -> QueryClientProvider -> AuthProvider -> App

App (router, role-gated via ProtectedRoute):
  /login                       public
  /patients/register           ASHA only
  /screening/new                ASHA only
  /screening/:id/result          ASHA only
  /referrals                      PHC_OFFICER only
  /dashboard                       DISTRICT_OFFICER only (lazy-loaded — see below)
```

- **API layer** (`src/api/`): thin Axios wrappers, one file per resource. All request/response shapes mirror backend Pydantic schemas field-for-field (`src/lib/types.ts`).
- **Auth** (`src/hooks/useAuth.tsx`): JWT persisted to `localStorage`, session restored on mount (after checking the token's own `exp` claim), auto-logout scheduled via `setTimeout` at the token's actual expiry, plus a reactive fallback — any `401` response also triggers logout via `api/axios.ts`'s interceptor.
- **Design system** (`src/components/ui/`): a bespoke healthcare-appropriate token system (medical blue / success / warning / danger / neutral) plus hand-built shadcn-convention primitives (Input, Button, Select, etc. — built by hand since `ui.shadcn.com`'s CLI registry wasn't reachable in the development environment, but follow the identical API shape).
- **Signature element**: `ConfidenceFingerprint` — the four-signal bar visualization is Arogent Verify's actual mechanism made visible, reused everywhere from compact list rows to the full Result screen.
- **Dashboard is lazy-loaded** (`React.lazy` + `Suspense` in `App.tsx`) since it's the only route that imports Recharts, the largest dependency — ASHA and PHC Officer sessions never download that chunk.

## Why These Architectural Choices

- **Thin routes, service-layer logic**: every router file just translates HTTP <-> service calls. Scoring, gating, and orchestration all live in `app/pipeline`, `app/verify`, `app/risk`, `app/referral` — testable without spinning up FastAPI at all.
- **Synthetic data with an explicit disclosure**: every AI-adjacent docstring and the README state plainly that no real clinical data is used, rather than letting that be assumed or discovered.
- **Explicit "what's not built" labeling**: rather than silently omitting requested functionality when the backend doesn't support it (e.g. a "Recent Screenings" dashboard table with no backing endpoint), the missing piece is built as a clearly labeled placeholder. See `README.md`'s "What's Deliberately Not Built" section for the full list.
