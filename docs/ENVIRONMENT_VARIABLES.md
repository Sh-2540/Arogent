# Environment Variables Reference

## Backend (`backend/.env`, see `backend/.env.example`)

Loaded via `pydantic-settings` in `backend/app/config.py`. Every field has a default, so the app runs with zero configuration for local development — but several defaults are explicitly **not safe** beyond that, marked below.

| Variable | Default | Required before deployment? | Notes |
|---|---|---|---|
| `SECRET_KEY` | `"dev-secret-key-change-in-production"` | **Yes — critical** | Signs every JWT. The default is hardcoded in this public codebase; leaving it unset in production means anyone can forge a valid token for any role. The app logs a loud warning at startup if this is still the default (see `app/main.py`). Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `DATABASE_URL` | `sqlite:///./arogent.db` | Recommended | SQLite is fine for a demo; a real deployment should point this at Postgres/MySQL (see `DEPLOYMENT.md`). |
| `CORS_ORIGINS` | `["http://localhost:5173","http://127.0.0.1:5173"]` | **Yes** | Must include your deployed frontend's exact origin (scheme + host + port), or every API call from the deployed frontend will fail. Pydantic-settings parses this as a JSON list from the env var string. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `720` (12 hours) | No | Tuned for a field worker's shift length. Shorten for tighter security at the cost of more frequent logins. |
| `ALGORITHM` | `HS256` | No | JWT signing algorithm. Explicitly pinned on both encode and decode — do not change without understanding the security implications (algorithm confusion attacks). |
| `APP_NAME` | `"Arogent API"` | No | Cosmetic — shown in Swagger UI title and startup logs. |
| `API_V1_PREFIX` | `/api/v1` | No | Changing this requires updating the frontend's `VITE_API_BASE_URL` to match. |
| `CONFIDENCE_HIGH_THRESHOLD` | `80.0` | No | Arogent Verify's HIGH confidence cutoff. Changing this changes clinical behavior — see `ARCHITECTURE.md` before touching. |
| `CONFIDENCE_MEDIUM_THRESHOLD` | `50.0` | No | Same caveat. |

## Frontend (`frontend/.env`, see `frontend/.env.example`)

Loaded via Vite's built-in `import.meta.env` (only variables prefixed `VITE_` are exposed to client code — this is a Vite security feature, not a project-specific choice).

| Variable | Default (if unset) | Required before deployment? | Notes |
|---|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000/api/v1` | **Yes** | The deployed backend's URL. Without this set correctly, a deployed frontend will try to call `127.0.0.1` from the user's own browser, which will always fail. |

## What's Intentionally Not an Environment Variable

- **Confidence Fingerprint weights** (35/30/20/15 split across the four signals) — hardcoded in `app/verify/aggregate.py`'s `BASE_WEIGHTS`. This is a clinical/product decision, not a deployment concern, so it's not exposed as configuration.
- **Symptom pool** — hardcoded in `app/ai/synthetic_data.py` and mirrored in `frontend/src/lib/symptoms.ts`. Changing this requires retraining Arogent Risk (the feature vector shape changes), so it's a code change, not a config toggle.
