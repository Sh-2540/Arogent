"""
Geographic Consistency (Arogent Verify signal 4 of 4).

Checks whether the screening location is consistent with the ASHA's
assigned service region — not a single village centroid, since villages
are geographically spread out and a centroid comparison can penalize a
perfectly legitimate screening at the edge of a large village.

Two independent checks, combined:
  1. Village-name match against the ASHA's assignment (always available)
  2. GPS distance from the village, if coordinates were submitted (optional
     — many field phones don't reliably provide this)

GPS is a refinement on top of the village-name check, not a separate
signal — when GPS is absent, the score is the village-name check alone
(this is not treated as "unavailable" for reweighting purposes, since a
useful geographic signal is still being produced, just a less precise one).

Note: working-hours timing lives in anomaly.py (Behaviour Consistency),
not here — it's a workflow-pattern check, not a location check.
"""
from __future__ import annotations

import math

from app.verify.schemas import VerifyInput, SignalResult

# Approximate radius (km) considered a normal service region around a village
# centroid — deliberately generous, since a "distance from assigned service
# region" check should tolerate real-world coverage patterns, not just a
# single point.
SERVICE_REGION_RADIUS_KM = 5.0

# Rough village centroids for the hackathon demo dataset — in production this
# would come from a proper geo-boundary dataset per Ayushman Arogya Mandir
# catchment, not a single lat/long point.
VILLAGE_CENTROIDS = {
    "Wadgaon": (19.95, 74.75),
    "Karanjgaon": (19.98, 74.80),
    "Shirsoli": (20.02, 74.72),
    "Manegaon": (19.90, 74.68),
    "Pimpri Budruk": (19.93, 74.85),
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def score_geographic_consistency(data: VerifyInput) -> SignalResult:
    score = 100.0
    flags: list[str] = []

    if data.village_at_screening != data.asha_assigned_village:
        # Moderate deduction only — ASHAs legitimately cover neighboring
        # villages sometimes. This is not treated as proof of anything.
        score -= 25
        flags.append(
            f"village_mismatch: screening logged in {data.village_at_screening!r}, "
            f"ASHA assigned to {data.asha_assigned_village!r}"
        )
    else:
        flags.append("village_matches_assignment")

    if data.latitude is not None and data.longitude is not None:
        centroid = VILLAGE_CENTROIDS.get(data.village_at_screening)
        if centroid:
            distance_km = _haversine_km(data.latitude, data.longitude, *centroid)
            if distance_km > SERVICE_REGION_RADIUS_KM:
                deduction = min(30, (distance_km - SERVICE_REGION_RADIUS_KM) * 3)
                score -= deduction
                flags.append(
                    f"outside_service_region: {distance_km:.1f} km from the assigned "
                    f"service region (expected within {SERVICE_REGION_RADIUS_KM} km)"
                )
    else:
        flags.append("gps_unavailable: checked by village name only")

    return SignalResult(score=max(score, 0.0), available=True, flags=flags)
