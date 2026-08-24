from pydantic import BaseModel, Field

from app.schemas.ship30 import Ship30Plan


class Ship30Request(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=10000,
    )


class Ship30Response(BaseModel):
    plan: Ship30Plan
