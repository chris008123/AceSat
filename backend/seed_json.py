from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.database.connection import SessionLocal
from app.models.question import Question


BASE_DIR = Path(__file__).resolve().parent
QUESTION_FILE = BASE_DIR / "data" / "acesat_question_bank_500.json"


def normalize_difficulty(value) -> int:
    """
    Convert the JSON difficulty labels into the integer format
    used by backend.app.models.question.Question.

    1 = Easy
    2 = Medium
    3 = Hard
    """
    if isinstance(value, int):
        return max(1, min(3, value))

    mapping = {
        "easy": 1,
        "medium": 2,
        "hard": 3,
    }

    return mapping.get(str(value).strip().lower(), 2)


def normalize_subject(value: str) -> str:
    """
    Keep the backend subject names consistent.
    """
    value = value.strip()

    if value.lower() in {"reading and writing", "reading", "english"}:
        return "Reading and Writing"

    if value.lower() == "math":
        return "Math"

    return value


def normalize_topic(question: dict) -> str:
    """
    Use the most specific topic available.

    The current backend Question model has no separate domain/subtopic
    columns, so topic becomes the grouping field used by session_service.
    """
    topic = question.get("topic")

    if topic:
        return str(topic).strip()

    domain = question.get("domain")

    if domain:
        return str(domain).strip()

    return "General"


def load_questions() -> list[dict]:
    if not QUESTION_FILE.exists():
        raise FileNotFoundError(
            f"Question bank not found:\n{QUESTION_FILE}"
        )

    with QUESTION_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Question bank must contain a JSON array.")

    return data


def seed_questions() -> None:
    questions = load_questions()

    print(f"Found {len(questions)} questions.")
    print("Starting database import...\n")

    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:
        for index, item in enumerate(questions, start=1):
            question_id = None

            answer_options = item.get("answer_options") or {}

            if not answer_options:
                print(
                    f"WARNING: Question {index} has no answer options. Skipping."
                )
                skipped += 1
                continue

            question = Question(
                subject=normalize_subject(
                    item.get("subject", "Unknown")
                ),
                topic=normalize_topic(item),
                difficulty=normalize_difficulty(
                    item.get("difficulty")
                ),
                question_text=item["question_text"],
                answer_options=answer_options,
                correct_answer=str(
                    item["correct_answer"]
                ),
                explanation=item.get("explanation"),
            )

            db.add(question)
            inserted += 1

            if inserted % 50 == 0:
                print(f"Inserted {inserted} questions...")

        db.commit()

        print("\n================================")
        print("QUESTION BANK IMPORT COMPLETE")
        print("================================")
        print(f"Total in file : {len(questions)}")
        print(f"Inserted      : {inserted}")
        print(f"Skipped       : {skipped}")
        print("================================")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()