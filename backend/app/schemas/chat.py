from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.ship30 import Ship30Plan


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10000,
    )

    agent: str = Field(
        default="chat",
        min_length=1,
        max_length=100,
    )


class ChatSource(BaseModel):
    guest: str | None = None
    title: str | None = None
    url: str | None = None
    distance: float | None = None
    chunk_index: int | None = None
    evidence_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    plan: Ship30Plan | None = None
    artifact_id: UUID | None = None
