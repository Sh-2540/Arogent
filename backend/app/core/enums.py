"""
Shared enums used across models, schemas, services, and API responses.

Centralizing these here means a status value is defined once and only
once — no magic strings scattered across the codebase, and the frontend
constants in `frontend/src/lib/constants.ts` are kept in sync with these
by convention (see the comment at the top of that file).
"""
from enum import Enum


class ConfidenceStatus(str, Enum):
    """Output of Arogent Verify — how much confidence to place in a screening record."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class RiskLevel(str, Enum):
    """Output of Arogent Risk — diabetes risk category. Only ever set when
    the linked screening's ConfidenceStatus is HIGH or MEDIUM."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class ReferralStatus(str, Enum):
    """Lifecycle of a referral generated after a HIGH RiskLevel result."""
    PENDING = "PENDING"
    REFERRED = "REFERRED"
    COMPLETED = "COMPLETED"


class UserRole(str, Enum):
    """Roles recognized by the auth system. Role-based access is enforced
    in Module 5 (API routes) — defined here so it's available everywhere."""
    ASHA = "ASHA"
    PHC_OFFICER = "PHC_OFFICER"
    DISTRICT_OFFICER = "DISTRICT_OFFICER"


# Screening Confidence Score → ConfidenceStatus thresholds.
# Mirrors app.config.settings so both the enum module and settings agree
# on where the cutoffs sit; settings values are the single source of truth,
# these are just the documented default here for readability.
CONFIDENCE_HIGH_THRESHOLD = 80.0
CONFIDENCE_MEDIUM_THRESHOLD = 50.0
