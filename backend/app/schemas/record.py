from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Version Schemas ──────────────────────────────────────────────────────────

class VersionBase(BaseModel):
    content: str
    change_note: Optional[str] = None
    is_ai_generated: Optional[bool] = True


class VersionCreate(VersionBase):
    pass


class VersionOut(VersionBase):
    id: int
    record_id: int
    version_number: int
    is_ai_generated: bool
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Record Schemas ────────────────────────────────────────────────────────────

class RecordCreate(BaseModel):
    title: str = Field(..., max_length=200)
    platform: str = Field(..., max_length=50)
    content: Optional[str] = None
    status: Optional[str] = Field("draft", max_length=20)  # draft / published / archived


class RecordUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    platform: Optional[str] = Field(None, max_length=50)
    content: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)


class RecordOut(BaseModel):
    id: int
    user_id: int
    title: str
    platform: str
    content: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    versions: List[VersionOut] = []

    model_config = {"from_attributes": True}


class RecordListItem(BaseModel):
    """精简版，用于列表展示"""
    id: int
    title: str
    platform: str
    status: str
    created_at: datetime
    updated_at: datetime
    version_count: int = 0

    model_config = {"from_attributes": True}