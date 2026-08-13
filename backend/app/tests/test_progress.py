from __future__ import annotations


def test_dashboard_with_no_history_degrades_gracefully(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    response = client.get("/progress/dashboard", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["weak_area"] is None
    assert body["streak"] == 0
    assert body["improvement"] == "+0"


def test_dashboard_reflects_completed_sessions(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)

    start = client.post("/sessions/start", headers=auth_headers)
    session_id = start.json()["session_id"]
    client.post(
        f"/sessions/complete?session_id={session_id}",
        json={"accuracy": 75, "duration": 30},
        headers=auth_headers,
    )

    response = client.get("/progress/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["streak"] == 1


def test_weekly_report_with_no_sessions(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    response = client.get("/progress/report", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["study_hours"] == 0
    assert body["questions_completed"] == 0
    assert body["recommendation"]


def test_weekly_report_reflects_session_duration(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    start = client.post("/sessions/start", headers=auth_headers)
    session_id = start.json()["session_id"]
    client.post(
        f"/sessions/complete?session_id={session_id}",
        json={"accuracy": 90, "duration": 60},
        headers=auth_headers,
    )

    response = client.get("/progress/report", headers=auth_headers)
    assert response.json()["study_hours"] == 1.0
