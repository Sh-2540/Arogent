# Folder Structure

130 source files total (Python + TypeScript/TSX, excluding `venv`/`node_modules`/`__pycache__`).

```
arogent/
├── README.md                    Top-level overview, quick start, doc index
├── .gitignore
│
├── docs/                        This documentation set
│   ├── INSTALLATION.md
│   ├── LOCAL_DEVELOPMENT.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── FOLDER_STRUCTURE.md      (this file)
│   ├── ENVIRONMENT_VARIABLES.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md
│
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── main.py               FastAPI entrypoint, lifespan, CORS, router registration
│   │   ├── config.py             Settings (env-var driven, pydantic-settings)
│   │   ├── database.py           SQLAlchemy engine/session/Base
│   │   │
│   │   ├── core/                 Cross-cutting: enums, auth primitives
│   │   │   ├── enums.py          ConfidenceStatus, RiskLevel, ReferralStatus, UserRole
│   │   │   └── security.py       Password hashing, JWT, get_current_user, require_roles
│   │   │
│   │   ├── models/                SQLAlchemy ORM models (one file per table)
│   │   │   ├── user.py, patient.py, screening.py, referral.py
│   │   │
│   │   ├── schemas/                Pydantic request/response schemas (mirrors models/)
│   │   │   ├── user.py, patient.py, screening.py, referral.py, dashboard.py
│   │   │
│   │   ├── verify/                 Arogent Verify — independent package, see ARCHITECTURE.md
│   │   │   ├── rules.py            Clinical Consistency
│   │   │   ├── historical.py       Historical Consistency
│   │   │   ├── anomaly.py          Behaviour Consistency (deterministic + Isolation Forest)
│   │   │   ├── geographic.py       Geographic Consistency
│   │   │   ├── aggregate.py        Weighted scoring, status/recommendation mapping
│   │   │   ├── explain.py          Deterministic explanation bullets
│   │   │   ├── service.py          Orchestrates the above; only module that touches the DB
│   │   │   └── schemas.py
│   │   │
│   │   ├── risk/                   Arogent Risk — independent package
│   │   │   ├── model.py            Loads the trained model (Logistic Regression or XGBoost)
│   │   │   ├── features.py         Feature vector building, per-prediction contributions
│   │   │   ├── service.py          predict_diabetes_risk() — enforces the confidence gate
│   │   │   └── schemas.py
│   │   │
│   │   ├── referral/                Referral Engine — independent package
│   │   │   └── service.py            generate_referral()
│   │   │
│   │   ├── pipeline/                 Pipeline Orchestrator — the ONLY place Verify/Risk/Referral are composed
│   │   │   └── service.py
│   │   │
│   │   ├── services/                  Non-pipeline services (CRUD, not scoring/gating)
│   │   │   ├── auth_service.py, patient_service.py, referral_service.py, dashboard_service.py
│   │   │
│   │   ├── routers/                    FastAPI route handlers — thin, delegate to services
│   │   │   ├── auth.py, patients.py, screenings.py, referrals.py, dashboard.py
│   │   │
│   │   └── ai/                          Model training scripts + synthetic data (offline, not runtime)
│   │       ├── synthetic_data.py         Generates the synthetic dataset — explicit disclosure at top
│   │       ├── train_anomaly_model.py    Trains Arogent Verify's Isolation Forest
│   │       ├── risk_features.py          Feature engineering shared between training and runtime
│   │       ├── train_risk_model.py       Trains + compares Arogent Risk's LogReg vs XGBoost
│   │       └── models/                    Saved model artifacts (.joblib, .json) — gitignored
│   │
│   └── tests/
│       ├── verify/    57 tests — rules, historical, geographic, anomaly, aggregate, explain, service
│       ├── risk/       16 tests — confidence gate, risk levels, DB integration
│       └── api/         20 tests — auth, RBAC, full end-to-end pipeline via TestClient
│
└── frontend/
    ├── package.json
    ├── .env.example
    ├── vite.config.ts, tsconfig.app.json (strict mode enabled)
    └── src/
        ├── main.tsx                BrowserRouter + QueryClientProvider + AuthProvider
        ├── App.tsx                 Route definitions, role-gated
        ├── index.css               Design tokens (@theme block — colors, type, focus states)
        │
        ├── api/                    Axios wrappers, one file per resource
        │   ├── axios.ts             Instance + interceptors (token attach, 401 handling)
        │   ├── auth.ts, patients.ts, screenings.ts, dashboard.ts
        │
        ├── hooks/
        │   ├── useAuth.tsx           Auth context — persistence, session restore, auto-logout
        │   └── useDashboard.ts        Combines dashboard summary + referrals queries
        │
        ├── lib/
        │   ├── types.ts               TS types mirroring backend Pydantic schemas
        │   ├── constants.ts            Shared enums (mirrors backend/app/core/enums.py)
        │   ├── symptoms.ts              Mirrors backend's SYMPTOM_POOL exactly
        │   ├── chartColors.ts            Chart hex values, matching badge design tokens
        │   ├── queryClient.ts             React Query client config
        │   ├── utils.ts                    cn() class-merging utility
        │   └── validation/                  Zod schemas (mirror backend Pydantic validation)
        │       ├── authSchemas.ts, patientSchemas.ts, screeningSchemas.ts
        │
        ├── components/
        │   ├── layout/          AppShell, TopBar, Sidebar (role-aware nav)
        │   ├── auth/              ProtectedRoute
        │   ├── patients/           PatientSearchSelect
        │   ├── dashboard/            ConfidenceChart, RiskDistributionChart, ReferralChart,
        │   │                          VillageHotspotChart, RecentScreeningsTable
        │   ├── ui/                     Design system: Card, badges, ConfidenceFingerprint
        │   │                            (signature element), shadcn-convention primitives
        │   │                            (lowercase filenames: button.tsx, input.tsx, etc.)
        │   └── index.ts                  Central barrel export
        │
        └── pages/
            ├── LoginPage.tsx, RegisterPatientPage.tsx
            ├── ScreeningFormPage.tsx, ScreeningResultPage.tsx
            ├── DashboardPage.tsx (lazy-loaded from App.tsx)
            ├── PlaceholderPage.tsx, UnauthorizedPage.tsx
```

## Naming Conventions (verified consistent, not just asserted)

- **Backend**: all files/modules snake_case (Python convention)
- **Frontend components**: PascalCase for domain components (`Card.tsx`, `ConfidenceBadge.tsx`); lowercase for shadcn-convention primitives (`button.tsx`, `input.tsx`) — this split is intentional, signaling "hand-rolled shadcn-style primitive" vs. "domain component," not an inconsistency
- **Frontend hooks**: `useX.tsx`/`useX.ts` pattern throughout
- **Frontend API files**: lowercase, one file per backend resource
