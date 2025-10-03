"""
Authentication tests
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """Authentication test cases"""

    def test_register_user(self, client: TestClient):
        """Test user registration"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }

        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 200

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient):
        """Test registration with duplicate email"""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }

        # First registration
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 200

        # Duplicate registration
        user_data["username"] = "user2"  # Different username
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 400

    def test_login_success(self, client: TestClient):
        """Test successful login"""
        # First register a user
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "first_name": "Login",
            "last_name": "User",
            "password": "loginpassword123",
        }

        register_response = client.post("/api/v1/register", json=user_data)
        assert register_response.status_code == 200

        # Then login
        login_data = {"email": "login@example.com", "password": "loginpassword123"}

        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["token"]["token_type"] == "bearer"
        assert "access_token" in data["token"]

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

        response = client.post("/api/v1/login", json=login_data)
        assert response.status_code == 401
