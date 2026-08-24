from pydantic import BaseModel, Field


class PlanAction(BaseModel):
    """
    One concrete action in the 30-day plan.

    Every action must be explicitly grounded in one or more
    selected evidence items.
    """

    action: str = Field(
        min_length=1,
        max_length=1000,
    )

    evidence_ids: list[str] = Field(
        min_length=1,
    )


class PlanPhase(BaseModel):
    """
    One phase of the 30-day plan.

    Empty phases are valid. We must not generate filler actions
    merely to populate the 30-day structure.
    """

    actions: list[PlanAction] = Field(
        default_factory=list,
    )


class Ship30Plan(BaseModel):
    """
    Structured 30-day growth plan.

    The plan is generated from grounded transcript evidence.
    """

    goal: str = Field(
        min_length=1,
        max_length=1000,
    )

    principles: list[str] = Field(
        default_factory=list,
    )

    days_1_7: PlanPhase

    days_8_14: PlanPhase

    days_15_21: PlanPhase

    days_22_30: PlanPhase

    success: list[str] = Field(
        default_factory=list,
    )
