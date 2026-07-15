"""
Import every model here so Base.metadata is fully populated before
Base.metadata.create_all() runs in app.main's startup event.
"""
from app.models.user import User
from app.models.patient import Patient
from app.models.screening import Screening
from app.models.referral import Referral

__all__ = ["User", "Patient", "Screening", "Referral"]
