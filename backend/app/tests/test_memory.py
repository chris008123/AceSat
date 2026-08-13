from __future__ import annotations


def test_store_and_retrieve_memory(client, auth_headers):
    profile = client.post(
        "/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers
    ).json()

    response = client.post(
        "/memory/update",
        json={"type": "academic", "data": {"weak_topic": "Reading Inference", "strength": "Vocabulary"}},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Need the student's own profile id (not user id) for the retrieve
    # path — fetch it back out via /students/profile isn't exposed, so
    # pull it from the DB the same way the route does: re-derive through
    # another store call's implicit profile lookup is redundant; instead
    # assert retrieval works by calling the endpoint with the id embedded
    # in a second store's implicit context. Simpler: use the auth'd
    # get-profile-adjacent path by checking memory list is non-empty via
    # the same session.
    from app.database.connection import SessionLocal
    from app.models.student import StudentProfile
    from app.models.user import User

    db = SessionLocal()
    user = db.query(User).filter_by(email="sarah@email.com").first()
    student_profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    student_id = str(student_profile.id)
    db.close()

    response = client.get(f"/memory/student/{student_id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body["memories"]) == 1
    assert body["memories"][0]["type"] == "academic"
    assert body["memories"][0]["data"]["weak_topic"] == "Reading Inference"


def test_store_invalid_memory_type_rejected(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    response = client.post(
        "/memory/update",
        json={"type": "not_a_real_type", "data": {}},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_retrieve_another_students_memory_rejected(client, auth_headers):
    client.post("/students/profile", json={"target_score": 1450, "study_time": 45}, headers=auth_headers)
    fake_student_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/memory/student/{fake_student_id}", headers=auth_headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_ERROR"
