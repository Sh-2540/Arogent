/**
 * Shared constants used across pages, components, and API response types.
 *
 * These values must stay in sync with `backend/app/core/enums.py` — if you
 * add or rename a value on one side, update the other. Keeping them as
 * `as const` objects (rather than TS `enum`) makes the values easy to use
 * directly as string literals when talking to the API, since FastAPI/Pydantic
 * serialize the Python enums as plain strings.
 */

/** Output of Arogent Verify — how much confidence to place in a screening record. */
export const ConfidenceStatus = {
  HIGH: "HIGH",
  MEDIUM: "MEDIUM",
  LOW: "LOW",
  NEEDS_REVIEW: "NEEDS_REVIEW",
} as const;
export type ConfidenceStatus = (typeof ConfidenceStatus)[keyof typeof ConfidenceStatus];

/** Output of Arogent Risk — diabetes risk category. */
export const RiskLevel = {
  LOW: "LOW",
  MODERATE: "MODERATE",
  HIGH: "HIGH",
} as const;
export type RiskLevel = (typeof RiskLevel)[keyof typeof RiskLevel];

/** Lifecycle of a referral generated after a HIGH RiskLevel result. */
export const ReferralStatus = {
  PENDING: "PENDING",
  REFERRED: "REFERRED",
  COMPLETED: "COMPLETED",
} as const;
export type ReferralStatus = (typeof ReferralStatus)[keyof typeof ReferralStatus];

/** Roles recognized by the auth system. */
export const UserRole = {
  ASHA: "ASHA",
  PHC_OFFICER: "PHC_OFFICER",
  DISTRICT_OFFICER: "DISTRICT_OFFICER",
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

/** Mirrors backend/app/core/enums.py thresholds — for any client-side display logic only; the backend is the source of truth for the actual classification. */
export const CONFIDENCE_HIGH_THRESHOLD = 80;
export const CONFIDENCE_MEDIUM_THRESHOLD = 50;
