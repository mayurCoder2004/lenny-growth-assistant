from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    user_id: UUID
    title: str = Field(
        default="New Chat",
        min_length=1,
        max_length=255,
    )


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MessageCreate(BaseModel):
    role: str = Field(
        min_length=1,
        max_length=20,
    )

    content: str = Field(
        min_length=1,
    )


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }