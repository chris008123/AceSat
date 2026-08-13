from app.api.routes.ai import router as ai_router
from app.api.routes.assessment import router as assessment_router
from app.api.routes.auth import router as auth_router
from app.api.routes.students import router as students_router

__all__ = ["ai_router", "assessment_router", "auth_router", "students_router"]
