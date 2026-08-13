"""Importing all backend-owned models together here ensures SQLAlchemy's
declarative registry can resolve string-based relationship() references
(e.g. User.student_profile <-> StudentProfile.user) regardless of which
module gets imported first elsewhere in the app.
"""

from app.models.question import Question
from app.models.student import StudentProfile
from app.models.user import User, UserRole

__all__ = ["Question", "StudentProfile", "User", "UserRole"]
