from __future__ import annotations


def test_full_assessment_flow(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)

    start = client.post("/assessment/start", headers=auth_headers)
    assert start.status_code == 200
    body = start.json()
    assessment_id = body["assessment_id"]
    assert len(body["questions"]) > 0

    # Answer the first returned question with a deliberately wrong answer
    # to exercise both branches of the correctness check.
    question = body["questions"][0]
    answer = client.post(
        f"/assessment/answer?assessment_id={assessment_id}",
        json={"question_id": question["id"], "answer": "Z", "confidence": 3, "time_taken": 20},
        headers=auth_headers,
    )
    assert answer.status_code == 200
    assert answer.json()["correct"] is False

    for q in body["questions"][1:]:
        client.post(
            f"/assessment/answer?assessment_id={assessment_id}",
            json={"question_id": q["id"], "answer": "A", "confidence": 3, "time_taken": 20},
            headers=auth_headers,
        )

    complete = client.post(f"/assessment/complete?assessment_id={assessment_id}", headers=auth_headers)
    assert complete.status_code == 200
    assert complete.json()["status"] == "completed"
    assert 0 <= complete.json()["score"] <= 100


def test_complete_assessment_with_no_answers_rejected(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    start = client.post("/assessment/start", headers=auth_headers)
    assessment_id = start.json()["assessment_id"]

    response = client.post(f"/assessment/complete?assessment_id={assessment_id}", headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_answer_unknown_assessment_returns_session_error(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    fake_assessment_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/assessment/answer?assessment_id={fake_assessment_id}",
        json={"question_id": str(seeded_questions[0].id), "answer": "A", "confidence": 3, "time_taken": 20},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SESSION_ERROR"
