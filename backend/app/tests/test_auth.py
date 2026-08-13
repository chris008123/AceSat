from __future__ import annotations


def test_register_creates_account(client):
    response = client.post("/auth/register", json={"email": "sarah@email.com", "password": "supersecure1"})
    assert response.status_code == 200
    body = response.json()
    assert "user_id" in body


def test_register_duplicate_email_rejected(client):
    client.post("/auth/register", json={"email": "sarah@email.com", "password": "supersecure1"})
    response = client.post("/auth/register", json={"email": "sarah@email.com", "password": "different1"})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_login_returns_token(client):
    client.post("/auth/register", json={"email": "sarah@email.com", "password": "supersecure1"})
    response = client.post("/auth/login", json={"email": "sarah@email.com", "password": "supersecure1"})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user_id"]


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={"email": "sarah@email.com", "password": "supersecure1"})
    response = client.post("/auth/login", json={"email": "sarah@email.com", "password": "wrongpassword"})
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTH_ERROR"


def test_protected_route_requires_token(client):
    response = client.get("/students/profile")
    assert response.status_code in (401, 403)
