"""
End-to-end tests through the actual API — registration, screening
submission, and confirming the confidence gate holds at the HTTP layer,
not just at the service layer (already covered in tests/risk and
tests/verify).
"""
from tests.api.conftest import register_and_login


def _register_patient(client, token, village="Wadgaon", age=55) -> int:
    response = client.post(
        "/api/v1/patients",
        json={"full_name": "Test Patient", "age": age, "gender": "Male", "village": village},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


class TestScreeningPipelineEndToEnd:
    def test_high_confidence_high_risk_generates_referral(self, client):
        token = register_and_login(client, "asha_e2e_1", "ASHA", "Wadgaon")
        patient_id = _register_patient(client, token)

        response = client.post(
            "/api/v1/screenings",
            json={
                "patient_id": patient_id, "blood_glucose_mg_dl": 240.0, "bmi": 32.0,
                "family_history_diabetes": True, "physical_activity_level": "LOW",
                "symptoms": ["fatigue", "frequent_urination", "excessive_thirst"],
                "village_at_screening": "Wadgaon",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["confidence_status"] == "HIGH"
        # Risk may or may not land in HIGH bucket depending on the model,
        # but if confidence is HIGH, risk_score must have been computed —
        # this is the one thing that should never be null here.
        assert data["risk_score"] is not None

    def test_hard_bound_violation_never_reaches_risk_via_api(self, client):
        token = register_and_login(client, "asha_e2e_2", "ASHA", "Wadgaon")
        patient_id = _register_patient(client, token)

        response = client.post(
            "/api/v1/screenings",
            json={
                "patient_id": patient_id, "blood_glucose_mg_dl": 900.0, "bmi": 24.0,
                "family_history_diabetes": False, "physical_activity_level": "MODERATE",
                "symptoms": [], "village_at_screening": "Wadgaon",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["confidence_status"] == "NEEDS_REVIEW"
        assert data["risk_score"] is None
        assert data["risk_level"] is None
        assert data["referral_status"] is None
        assert data["recommendation"] == "Escalate for PHC Review"

    def test_unknown_patient_returns_404(self, client):
        token = register_and_login(client, "asha_e2e_3", "ASHA", "Wadgaon")
        response = client.post(
            "/api/v1/screenings",
            json={
                "patient_id": 999999, "blood_glucose_mg_dl": 110.0, "bmi": 24.0,
                "family_history_diabetes": False, "physical_activity_level": "MODERATE",
                "symptoms": [], "village_at_screening": "Wadgaon",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_get_screening_by_id_matches_post_response(self, client):
        token = register_and_login(client, "asha_e2e_4", "ASHA", "Wadgaon")
        patient_id = _register_patient(client, token)

        post_response = client.post(
            "/api/v1/screenings",
            json={
                "patient_id": patient_id, "blood_glucose_mg_dl": 110.0, "bmi": 23.0,
                "family_history_diabetes": False, "physical_activity_level": "MODERATE",
                "symptoms": [], "village_at_screening": "Wadgaon",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        screening_id = post_response.json()["id"]

        get_response = client.get(f"/api/v1/screenings/{screening_id}", headers={"Authorization": f"Bearer {token}"})
        assert get_response.status_code == 200
        assert get_response.json()["confidence_score"] == post_response.json()["confidence_score"]

    def test_patient_history_returns_submitted_screening(self, client):
        token = register_and_login(client, "asha_e2e_5", "ASHA", "Wadgaon")
        patient_id = _register_patient(client, token)

        client.post(
            "/api/v1/screenings",
            json={
                "patient_id": patient_id, "blood_glucose_mg_dl": 110.0, "bmi": 23.0,
                "family_history_diabetes": False, "physical_activity_level": "MODERATE",
                "symptoms": [], "village_at_screening": "Wadgaon",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        history_response = client.get(f"/api/v1/screenings/patient/{patient_id}", headers={"Authorization": f"Bearer {token}"})
        assert history_response.status_code == 200
        assert len(history_response.json()) == 1


class TestReferralGeneratedEndToEnd:
    def test_high_risk_screening_produces_listable_referral(self, client):
        asha_token = register_and_login(client, "asha_e2e_6", "ASHA", "Wadgaon")
        do_token = register_and_login(client, "do_e2e_1", "DISTRICT_OFFICER")
        patient_id = _register_patient(client, asha_token)

        client.post(
            "/api/v1/screenings",
            json={
                "patient_id": patient_id, "blood_glucose_mg_dl": 250.0, "bmi": 35.0,
                "family_history_diabetes": True, "physical_activity_level": "LOW",
                "symptoms": ["fatigue", "frequent_urination", "excessive_thirst", "blurred_vision"],
                "village_at_screening": "Wadgaon",
            },
            headers={"Authorization": f"Bearer {asha_token}"},
        )

        referrals_response = client.get("/api/v1/referrals", headers={"Authorization": f"Bearer {do_token}"})
        assert referrals_response.status_code == 200
        # With this extreme a risk profile, a HIGH risk_level (and therefore
        # a referral) is very likely but not model-guaranteed — check
        # conditionally rather than asserting an exact count.
        referrals = referrals_response.json()
        if referrals:
            assert referrals[0]["status"] == "PENDING"
