"""Seed the `questions` table with a small starter question bank.

Added during frontend integration: the `questions` table ships empty, so
`/assessment/start` and `/sessions/start` had nothing to return — every
downstream screen (assessment, session, diagnosis, coach) needs at least
a few real questions per topic to work end to end.

Topics here match `ai-data/ai_data/knowledge/sample_concepts.json`
exactly (`Reading Inference`, `Linear Equations`, `Grammar`) so
`POST /ai/coach`'s lookup by weakest topic actually finds teaching
material, and there are >=3 questions per topic so ai-data's
weak/strong-topic detection (min 3 attempts) has enough signal.

Usage:
    cd backend
    python -m scripts.seed_questions          # uses settings.database_url
"""

from __future__ import annotations

from app.database.connection import Base, SessionLocal, engine
from app.models.question import Question

QUESTIONS: list[dict] = [
    # --- Reading Inference (reading) ---
    {
        "subject": "reading",
        "topic": "Reading Inference",
        "difficulty": 3,
        "question_text": (
            "\u201c...she watched him from the doorway a long moment before speaking, her hand "
            "still resting on the latch as if she might yet close it.\u201d Which choice best "
            "supports the idea that the narrator initially distrusts the visitor?"
        ),
        "answer_options": {
            "A": "She watched him from the doorway.",
            "B": "Her hand stayed on the latch, ready to close it.",
            "C": "She waited a long moment before speaking.",
            "D": "He stood outside until she noticed him.",
        },
        "correct_answer": "B",
        "explanation": (
            "The physical detail \u2014 her hand staying on the latch \u2014 is an action that "
            "reveals she's ready to shut him out. That's stronger evidence than description alone."
        ),
    },
    {
        "subject": "reading",
        "topic": "Reading Inference",
        "difficulty": 3,
        "question_text": (
            "\u201cHe said nothing, only turned the brim of his hat slowly between his fingers, "
            "and looked past her toward the fields.\u201d What does the visitor's prolonged "
            "silence most strongly suggest?"
        ),
        "answer_options": {
            "A": "He is admiring the scenery.",
            "B": "He is avoiding eye contact out of discomfort.",
            "C": "He has forgotten why he came.",
            "D": "He is waiting for her to speak first.",
        },
        "correct_answer": "B",
        "explanation": (
            "Turning his hat and looking away are both physical signs of unease \u2014 the "
            "passage is showing discomfort through action, not stating it directly."
        ),
    },
    {
        "subject": "reading",
        "topic": "Reading Inference",
        "difficulty": 2,
        "question_text": (
            "\u201cThe committee's report ran to four hundred pages, yet the mayor's public "
            "statement addressed only the two paragraphs favorable to her office.\u201d "
            "What can be inferred about the mayor's statement?"
        ),
        "answer_options": {
            "A": "It was a complete and fair summary of the report.",
            "B": "It selectively emphasized information favorable to her.",
            "C": "It was written by the committee itself.",
            "D": "It criticized the length of the report.",
        },
        "correct_answer": "B",
        "explanation": (
            "The contrast between \u201cfour hundred pages\u201d and \u201conly the two "
            "paragraphs\u201d is the evidence \u2014 it implies selective, self-serving emphasis."
        ),
    },
    {
        "subject": "reading",
        "topic": "Reading Inference",
        "difficulty": 4,
        "question_text": (
            "\u201cEach year he repainted the fence a shade lighter, though no one else seemed "
            "to notice the difference.\u201d This detail most strongly suggests that the "
            "character is"
        ),
        "answer_options": {
            "A": "indifferent to how the fence looks",
            "B": "attentive to small changes others overlook",
            "C": "trying to save money on paint",
            "D": "planning to sell the house soon",
        },
        "correct_answer": "B",
        "explanation": (
            "Noticing and acting on a change so subtle that \u201cno one else\u201d sees it "
            "signals a character who pays close attention to small details \u2014 the key "
            "inference is about his attentiveness, not his motive."
        ),
    },
    # --- Linear Equations (math) ---
    {
        "subject": "math",
        "topic": "Linear Equations",
        "difficulty": 2,
        "question_text": (
            "A rectangular garden has a perimeter of 60 feet. If the length is twice the "
            "width, what is the width?"
        ),
        "answer_options": {"A": "8 feet", "B": "10 feet", "C": "12 feet", "D": "15 feet"},
        "correct_answer": "B",
        "explanation": (
            "Setting up 2(w + 2w) = 60 gives 6w = 60, so w = 10. The setup \u2014 translating "
            "the sentence into an equation \u2014 is the real skill being tested here."
        ),
    },
    {
        "subject": "math",
        "topic": "Linear Equations",
        "difficulty": 2,
        "question_text": "Solve for x: 3(x + 2) = 5x - 4",
        "answer_options": {"A": "x = 3", "B": "x = 4", "C": "x = 5", "D": "x = 6"},
        "correct_answer": "C",
        "explanation": (
            "Distribute: 3x + 6 = 5x - 4. Move variables: 6 + 4 = 5x - 3x. Simplify: 10 = 2x. "
            "Divide: x = 5."
        ),
    },
    {
        "subject": "math",
        "topic": "Linear Equations",
        "difficulty": 3,
        "question_text": (
            "A phone plan charges a flat fee of $20 plus $0.10 per minute. If a customer's "
            "bill was $35, how many minutes did they use?"
        ),
        "answer_options": {"A": "100", "B": "125", "C": "150", "D": "175"},
        "correct_answer": "C",
        "explanation": (
            "20 + 0.10m = 35, so 0.10m = 15, and m = 150. Translating the flat fee and rate "
            "into an equation is the setup step that matters most."
        ),
    },
    {
        "subject": "math",
        "topic": "Linear Equations",
        "difficulty": 1,
        "question_text": "Solve for y: 2y - 7 = 11",
        "answer_options": {"A": "y = 7", "B": "y = 8", "C": "y = 9", "D": "y = 10"},
        "correct_answer": "C",
        "explanation": "Add 7 to both sides: 2y = 18. Divide by 2: y = 9.",
    },
    # --- Grammar (writing) ---
    {
        "subject": "writing",
        "topic": "Grammar",
        "difficulty": 2,
        "question_text": "Choose the correctly punctuated sentence.",
        "answer_options": {
            "A": "Although the exam was long, she finished early.",
            "B": "Although the exam was long she finished early.",
            "C": "Although, the exam was long she finished early.",
            "D": "Although the exam was long. She finished early.",
        },
        "correct_answer": "A",
        "explanation": (
            "The sentence opens with a dependent clause (\u201cAlthough the exam was "
            "long\u201d), which requires a comma before the independent clause that follows."
        ),
    },
    {
        "subject": "writing",
        "topic": "Grammar",
        "difficulty": 2,
        "question_text": (
            "Choose the choice that correctly completes the sentence: \u201cNeither the "
            "coach nor the players ___ satisfied with the result.\u201d"
        ),
        "answer_options": {"A": "was", "B": "were", "C": "is", "D": "has been"},
        "correct_answer": "B",
        "explanation": (
            "With \u201cneither...nor,\u201d the verb agrees with the closer subject "
            "(\u201cplayers,\u201d plural), so \u201cwere\u201d is correct."
        ),
    },
    {
        "subject": "writing",
        "topic": "Grammar",
        "difficulty": 3,
        "question_text": "Which choice uses the apostrophe correctly?",
        "answer_options": {
            "A": "The dog's chased its' tail.",
            "B": "The dogs chased its tail.",
            "C": "The dog chased its tail.",
            "D": "The dog chased it's tail.",
        },
        "correct_answer": "C",
        "explanation": (
            "\u201cIts\u201d (no apostrophe) is possessive; \u201cit's\u201d always means "
            "\u201cit is.\u201d Here the dog is chasing something belonging to it, so the "
            "possessive \u201cits\u201d with no apostrophe is correct."
        ),
    },
    {
        "subject": "writing",
        "topic": "Grammar",
        "difficulty": 2,
        "question_text": (
            "Choose the choice that correctly joins the two independent clauses: "
            "\u201cThe museum was closing___ we still had three galleries left to see.\u201d"
        ),
        "answer_options": {
            "A": ", but",
            "B": "but",
            "C": ", and",
            "D": "; however",
        },
        "correct_answer": "A",
        "explanation": (
            "Two independent clauses joined by a coordinating conjunction like \u201cbut\u201d "
            "need a comma before it."
        ),
    },
]


def seed() -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Question).count()
        if existing > 0:
            print(f"questions table already has {existing} row(s) — skipping seed.")
            return 0

        for row in QUESTIONS:
            db.add(Question(**row))
        db.commit()
        print(f"Seeded {len(QUESTIONS)} questions.")
        return len(QUESTIONS)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
