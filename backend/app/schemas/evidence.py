from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """
    A transcript chunk that has been selected as evidence.

    Retrieval produces candidates.
    Grounding produces selected evidence.
    """

    evidence_id: str = Field(min_length=1)

    source_id: str = Field(min_length=1)

    guest: str | None = None

    title: str | None = None

    content: str = Field(min_length=1)

    chunk_index: int | None = None

    url: str | None = None

    distance: float | None = None
