import pytest

from tests.api.conftest import register_and_login


class TestPatientRegistrationRBAC:
    def test_asha_can_register_patient(self, client):
        token = register_and_login(client, "asha1", "ASHA", "Wadgaon")
        response = client.post(
            "/api/v1/patients",
            json={"full_name": "Patient A", "age": 45, "gender": "Female", "village": "Wadgaon"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    @pytest.mark.parametrize("role", ["PHC_OFFICER", "DISTRICT_OFFICER"])
    def test_non_asha_roles_cannot_register_patient(self, client, role):
        token = register_and_login(client, f"user_{role.lower()}", role)
        response = client.post(
            "/api/v1/patients",
            json={"full_name": "Patient A", "age": 45, "gender": "Female", "village": "Wadgaon"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


class TestDashboardRBAC:
    def test_district_officer_can_access_dashboard(self, client):
        token = register_and_login(client, "do1", "DISTRICT_OFFICER")
        response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    @pytest.mark.parametrize("role", ["ASHA", "PHC_OFFICER"])
    def test_other_roles_cannot_access_dashboard(self, client, role):
        token = register_and_login(client, f"dashuser_{role.lower()}", role)
        response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403


class TestReferralUpdateRBAC:
    def test_asha_cannot_update_referral_status(self, client):
        token = register_and_login(client, "asha2", "ASHA", "Wadgaon")
        response = client.patch(
            "/api/v1/referrals/1", json={"status": "REFERRED"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_phc_officer_can_attempt_referral_update(self, client):
        # Referral doesn't exist -> 404, but this confirms the role check
        # itself passes (a 403 here would mean RBAC wrongly blocked a PHC officer).
        token = register_and_login(client, "phc1", "PHC_OFFICER")
        response = client.patch(
            "/api/v1/referrals/99999", json={"status": "REFERRED"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
