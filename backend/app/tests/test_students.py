from __future__ import annotations


def test_create_and_get_profile(client, auth_headers):
    response = client.post(
        "/students/profile",
        json={"target_score": 1450, "study_time": 45, "current_score": 1080},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["target_score"] == 1450
    assert body["study_time"] == 45

    response = client.get("/students/profile", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["current_score"] == 1080


def test_update_profile(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1400, "study_time": 30}, headers=auth_headers)
    response = client.put("/students/profile", json={"target_score": 1500}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["target_score"] == 1500
    assert response.json()["study_time"] == 30  # unchanged fields stay put


def test_get_profile_before_creation_returns_404(client, auth_headers):
    response = client.get("/students/profile", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
