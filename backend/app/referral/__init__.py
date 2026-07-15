"""Referral Engine — generates a tangible Referral record from a HIGH risk result."""
from app.referral.service import generate_referral, build_referral_reason

__all__ = ["generate_referral", "build_referral_reason"]
