

class TestRegister:
    def test_register_returns_201_and_user_data(self, client):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Sunita Patil", "username": "sunita_asha", "password": "pass123",
            "role": "ASHA", "assigned_village": "Wadgaon",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "sunita_asha"
        assert data["role"] == "ASHA"
        assert "hashed_password" not in data  # never leak the hash

    def test_duplicate_username_returns_409(self, client):
        payload = {"full_name": "A", "username": "dupe", "password": "pass123", "role": "ASHA"}
        client.post("/api/v1/auth/register", json=payload)
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409


class TestLogin:
    def test_correct_credentials_returns_token(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "A", "username": "loginuser", "password": "pass123", "role": "ASHA",
        })
        response = client.post("/api/v1/auth/login", data={"username": "loginuser", "password": "pass123"})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_wrong_password_returns_401(self, client):
        client.post("/api/v1/auth/register", json={
            "full_name": "A", "username": "wrongpassuser", "password": "pass123", "role": "ASHA",
        })
        response = client.post("/api/v1/auth/login", data={"username": "wrongpassuser", "password": "nope"})
        assert response.status_code == 401

    def test_unknown_username_returns_401(self, client):
        response = client.post("/api/v1/auth/login", data={"username": "ghost", "password": "pass123"})
        assert response.status_code == 401


class TestProtectedEndpointsRequireAuth:
    def test_patients_endpoint_requires_token(self, client):
        response = client.post("/api/v1/patients", json={"full_name": "X", "age": 30, "gender": "Male", "village": "Wadgaon"})
        assert response.status_code == 401
