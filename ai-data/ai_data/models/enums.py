"""Shared enums for the AI/Data layer.

Kept intentionally small and hackathon-appropriate — extend only when a
real requirement shows up in the docs or from the Backend/AI Agent
Engineers, per the "do not optimize for complexity" rule.
"""

from enum import Enum


class Subject(str, Enum):
    MATH = "math"
    READING = "reading"
    WRITING = "writing"  # grammar / language conventions


class DifficultyLevel(int, Enum):
    """1 = easiest, 5 = hardest. Matches `questions.difficulty` (Integer)
    in 10_Database_Design.md."""

    BEGINNER = 1
    EASY = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    GRID_IN = "grid_in"  # SAT math free-response


class ConfidenceLevel(str, Enum):
    """Matches the `answers.confidence` field described in
    10_Database_Design.md (used for the "AI Confidence System")."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MasteryTrend(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    WEAK = "weak"
    DECLINING = "declining"
    INSUFFICIENT_DATA = "insufficient_data"


class MemoryType(str, Enum):
    """Matches `ai_memory.memory_type` in 10_Database_Design.md."""

    ACADEMIC = "academic"
    BEHAVIOR = "behavior"
    PREFERENCE = "preference"
    GOAL = "goal"


class RecommendationAction(str, Enum):
    PRACTICE_TOPIC = "practice_topic"
    REVIEW_CONCEPT = "review_concept"
    TAKE_ASSESSMENT = "take_assessment"
    INCREASE_DIFFICULTY = "increase_difficulty"
    DECREASE_DIFFICULTY = "decrease_difficulty"
    STUDY_SESSION = "study_session"
    REST_REVIEW = "rest_review"
