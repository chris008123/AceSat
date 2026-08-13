"""Memory routes — Api_design.txt §11.

`GET /memory/student/{id}` in the doc takes an arbitrary `{id}` — scoped
here to the authenticated student's own id, since there's no admin/teacher
role wired up yet (Database_design.txt §5.1's `role` enum has
Student/Admin, but nothing in this backend currently checks for Admin).
Revisit this restriction once an admin role actually exists.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.memory import RetrieveMemoryResponse, StoreMemoryRequest, StoreMemoryResponse
from app.services import memory_bridge, student_service
from app.utils.errors import AuthError

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/update", response_model=StoreMemoryResponse)
def update(
    payload: StoreMemoryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StoreMemoryResponse:
    profile = student_service.get_profile(db, user.id)
    memory_bridge.store_memory(profile.id, payload.type, payload.data)
    return StoreMemoryResponse()


@router.get("/student/{student_id}", response_model=RetrieveMemoryResponse)
def get_memory(
    student_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RetrieveMemoryResponse:
    profile = student_service.get_profile(db, user.id)
    if str(profile.id) != student_id:
        raise AuthError("Cannot access another student's memory")

    entries = memory_bridge.retrieve_memory(profile.id)
    return RetrieveMemoryResponse(memories=entries)
