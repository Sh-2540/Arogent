# Security Review

Findings below come from reading the actual implementation (`app/core/security.py`, `app/config.py`, every router file, and grep-based scans for common vulnerability patterns) during Phase 10 — not a generic checklist filled in from memory.

## JWT Handling — Solid, One Real Gap

**What's correct:**
- Algorithm is explicitly pinned on both encode and decode (`algorithms=[settings.algorithm]`) — this prevents the classic "alg: none" / algorithm-confusion attack, where a naive verifier that doesn't pin the expected algorithm can be tricked into accepting an unsigned or differently-signed token.
- Expiry (`exp` claim) is set and enforced automatically by `python-jose`'s `jwt.decode()` — an expired token raises `JWTError`, caught and converted to a 401.
- Token payload only contains `sub` (user ID) — no unnecessary PII embedded in the token itself.

**Real gap:** there is no token revocation mechanism. If a token is compromised (stolen, leaked), it remains valid until its natural expiry (12 hours by default) — there's no server-side blacklist or way to force-invalidate it. For a healthcare app handling patient data, this is worth addressing in a future iteration (common mitigations: short-lived access tokens + refresh token rotation, or a revocation list checked on each request). **Not fixed in this phase** — it would be a new feature (session management), not a code-quality or documentation fix, and is out of Phase 10's stated scope.

## Password Hashing — Solid

`bcrypt` via `passlib`, the industry-standard choice (adaptive, salted, deliberately slow). Already had one real bug found and fixed in Module 5 (a `passlib`/`bcrypt` version incompatibility) — see `LOCAL_DEVELOPMENT.md`'s gotchas section. No further issues found.

## CORS Configuration — Correct

`allow_origins` is a specific whitelist (not a wildcard `*`), combined with `allow_credentials=True`. This is the secure pattern — browsers actually reject a wildcard origin combined with credentials, so this isn't just a preference, it's close to the only valid configuration once credentials are involved. Configurable per-deployment via the `CORS_ORIGINS` env var (see `ENVIRONMENT_VARIABLES.md`).

## Input Validation — Solid

Every endpoint validates input via Pydantic schemas (FastAPI's default behavior) — malformed requests are rejected with 422 before reaching any business logic. Zod schemas on the frontend mirror the same bounds, but the backend validation is the actual security boundary — client-side validation can always be bypassed by a direct API call, and the backend never trusts it.

## Authorization — Mostly Solid, Two Real Gaps

**What's correct:** every state-changing endpoint (`POST /patients`, `POST /screenings`, `PATCH /referrals/{id}`) requires the correct role via `require_roles()`. `GET /dashboard` correctly restricts to `DISTRICT_OFFICER`. Verified via a full endpoint-by-endpoint audit during this phase, not just spot-checked (see `API.md`'s auth column).

**Gap 1 — `POST /auth/register` is public.** Anyone can currently self-register as `DISTRICT_OFFICER` — the highest-privilege role in the system — with no restriction at all. This was a deliberate, documented trade-off from Module 5 for hackathon demo convenience ("this would itself be an admin-only action in production"), but it's a genuine must-fix-before-any-real-deployment item, not a minor note. **Not fixed in this phase** since restricting registration (e.g. requiring an existing District Officer to approve new accounts) is a new feature/workflow, outside this phase's "no new features" scope — but it's the single most important item in this document.

**Gap 2 — no row-level data scoping.** Authorization currently answers "what role are you," not "what data is actually yours." An authenticated ASHA can call `GET /patients?village=AnyVillage` and see patients outside their own assignment, or fetch any screening/referral by ID regardless of who registered it. This is a real patient-data-privacy concern for a healthcare tool, not a theoretical one. **Not fixed in this phase** — adding row-level scoping (e.g. filtering by `assigned_village`) is a behavior change to existing endpoints, which risks being treated as a feature change; documented here explicitly rather than fixed without going through the same review process every other module went through.

## Common Vulnerability Patterns — Checked, Clean

- **SQL injection:** zero raw SQL string interpolation found anywhere in the codebase (grepped for `execute(`, `.text(`, and f-string-built queries). Every query goes through SQLAlchemy's ORM query builder, which parameterizes automatically.
- **XSS:** zero usage of `dangerouslySetInnerHTML` or direct `innerHTML` manipulation anywhere in the frontend (grepped). React's default JSX rendering auto-escapes all text content.
- **Hardcoded secrets:** none found (grepped for common API key patterns). The one weak default (`SECRET_KEY`) is a documented fallback with a startup warning, not a silently-shipped secret.

## Rate Limiting — Not Implemented

No endpoint has rate limiting, including `POST /auth/login`. A public deployment is currently exposed to unlimited brute-force login attempts with no protection. This is listed in Phase 10's scope as "if possible" — it was not implemented, since adding it correctly (e.g. `slowapi` or a reverse-proxy-level solution) is closer to a new feature than a code-quality fix, and doing it hastily risks a shallow implementation that creates false confidence. Documented as a known gap rather than either skipped silently or half-implemented.

## Summary Table

| Area | Status |
|---|---|
| JWT algorithm/expiry handling | ✅ Correct |
| Token revocation | ⚠️ Not implemented — known gap |
| Password hashing | ✅ Correct |
| CORS | ✅ Correct |
| Input validation | ✅ Correct (backend is the real boundary) |
| Role-based authorization | ✅ Correct, where applied |
| Public registration endpoint | 🔴 Must fix before production |
| Row-level data scoping | 🔴 Must fix before production (real deployment) |
| SQL injection | ✅ Clean |
| XSS | ✅ Clean |
| Hardcoded secrets | ✅ Clean (one documented weak default with startup warning) |
| Rate limiting | ⚠️ Not implemented |
