"""Importing all backend-owned models together here ensures SQLAlchemy's
declarative registry can resolve string-based relationship() references
regardless of which module gets imported first elsewhere in the app.
"""

from app.models.assessment import Answer, Assessment
from app.models.learning_session import LearningSession
from app.models.progress import ProgressRecord
from app.models.question import Question
from app.models.student import StudentProfile
from app.models.study_plan import StudyPlan
from app.models.user import User, UserRole

__all__ = [
    "Answer",
    "Assessment",
    "LearningSession",
    "ProgressRecord",
    "Question",
    "StudentProfile",
    "StudyPlan",
    "User",
    "UserRole",
]
