from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10000,
    )


class ChatSource(BaseModel):
    guest: str | None = None
    title: str | None = None
    url: str | None = None
    distance: float | None = None
    chunk_index: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
