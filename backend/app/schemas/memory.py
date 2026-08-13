"""Matches Api_design.txt §11 (Store Memory / Retrieve Memory)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StoreMemoryRequest(BaseModel):
    type: str
    data: dict


class StoreMemoryResponse(BaseModel):
    message: str = "Memory stored"


class MemoryEntryResponse(BaseModel):
    type: str
    data: dict
    created_at: datetime


class RetrieveMemoryResponse(BaseModel):
    memories: list[MemoryEntryResponse]
