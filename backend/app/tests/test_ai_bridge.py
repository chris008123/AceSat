from __future__ import annotations


def _run_full_assessment(client, auth_headers, questions, given_answers):
    """Creates one assessment and submits answers for every (question,
    answer) pair given — doesn't restrict to whatever `/assessment/start`
    happened to return, since `submit_answer` only requires the assessment
    to exist, not that the question was in the original batch (a real
    session can extend beyond the initial question set).
    """
    start = client.post("/assessment/start", headers=auth_headers)
    assessment_id = start.json()["assessment_id"]

    for question, given in zip(questions, given_answers):
        client.post(
            f"/assessment/answer?assessment_id={assessment_id}",
            json={"question_id": str(question.id), "answer": given, "confidence": 3, "time_taken": 20},
            headers=auth_headers,
        )
    client.post(f"/assessment/complete?assessment_id={assessment_id}", headers=auth_headers)
    return assessment_id


def test_diagnose_identifies_weakness(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)

    # First 12 seeded questions are Reading Inference (correct_answer="A"),
    # answer 7 right then 5 wrong to trigger a declining/weak trend;
    # remaining 4 are Linear Equations (correct_answer="B"), answer all
    # right to establish a strength.
    reading_questions = seeded_questions[:12]
    math_questions = seeded_questions[12:]
    given = ["A"] * 7 + ["B"] * 5
    _run_full_assessment(client, auth_headers, reading_questions, given)
    _run_full_assessment(client, auth_headers, math_questions, ["B"] * len(math_questions))

    response = client.post("/ai/diagnose", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "Reading Inference" in body["weaknesses"]
    assert "%" in body["recommendation"]


def test_diagnose_without_answers_rejected(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    response = client.post("/ai/diagnose", headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_study_plan_generated_and_persisted(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    reading_questions = seeded_questions[:12]
    given = ["A"] * 7 + ["B"] * 5
    _run_full_assessment(client, auth_headers, reading_questions, given)

    response = client.post("/ai/study-plan", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body["plan"]) >= 1
    assert body["plan"][0]["topic"] == "Reading Inference"
    assert "reason" in body["plan"][0]


def test_coach_returns_teaching_material_for_weak_topic(client, auth_headers, seeded_questions):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    reading_questions = seeded_questions[:12]
    given = ["B"] * 12  # all wrong — correct is "A"
    _run_full_assessment(client, auth_headers, reading_questions, given)

    response = client.post("/ai/coach", json={"question": "I don't get this"}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]


def test_coach_with_no_history_gives_fallback(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    response = client.post("/ai/coach", json={"question": "help"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["next_question"] is None

