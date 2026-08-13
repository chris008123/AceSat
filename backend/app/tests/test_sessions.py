from __future__ import annotations


def test_start_session_returns_mission(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    response = client.post("/sessions/start", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"]
    assert body["mission"]


def test_start_session_mission_reflects_weak_topic(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)

    start = client.post("/assessment/start", headers=auth_headers)
    assessment_id = start.json()["assessment_id"]
    reading_questions = [q for q in seeded_questions if q.topic == "Reading Inference"]
    for q in reading_questions:
        client.post(
            f"/assessment/answer?assessment_id={assessment_id}",
            json={"question_id": str(q.id), "answer": "B", "confidence": 3, "time_taken": 20},
            headers=auth_headers,
        )
    client.post(f"/assessment/complete?assessment_id={assessment_id}", headers=auth_headers)

    response = client.post("/sessions/start", headers=auth_headers)
    assert "Reading Inference" in response.json()["mission"]


def test_complete_session(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    start = client.post("/sessions/start", headers=auth_headers)
    session_id = start.json()["session_id"]

    response = client.post(
        f"/sessions/complete?session_id={session_id}",
        json={"accuracy": 82, "duration": 40},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["accuracy"] == 82
    assert body["duration"] == 40


def test_complete_unknown_session_returns_session_error(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/sessions/complete?session_id={fake_id}",
        json={"accuracy": 50, "duration": 20},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SESSION_ERROR"


def test_complete_session_invalid_accuracy_rejected(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    start = client.post("/sessions/start", headers=auth_headers)
    session_id = start.json()["session_id"]

    response = client.post(
        f"/sessions/complete?session_id={session_id}",
        json={"accuracy": 150, "duration": 20},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
