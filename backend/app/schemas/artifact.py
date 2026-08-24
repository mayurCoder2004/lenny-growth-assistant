from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArtifactResponse(BaseModel):
    id: UUID
    session_id: UUID
    message_id: UUID | None
    type: str
    title: str
    content: str
    created_at: datetime
