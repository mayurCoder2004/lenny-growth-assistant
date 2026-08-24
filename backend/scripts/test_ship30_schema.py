from app.schemas.ship30 import (
    PlanAction,
    PlanPhase,
    Ship30Plan,
)


plan = Ship30Plan(
    goal="Improve onboarding activation",
    principles=[
        "Test onboarding before scaling implementation."
    ],
    days_1_7=PlanPhase(
        actions=[
            PlanAction(
                action="Test the onboarding flow with users.",
                evidence_ids=["lauryn-source-21"],
            )
        ]
    ),
    days_8_14=PlanPhase(
        actions=[]
    ),
    days_15_21=PlanPhase(
        actions=[]
    ),
    days_22_30=PlanPhase(
        actions=[]
    ),
    success=[
        "Evidence-supported onboarding improvements are tested."
    ],
)


print("=" * 70)
print("SHIP30 SCHEMA TEST")
print("=" * 70)
print(plan.model_dump_json(indent=2))
print()
print("SHIP30 SCHEMA TEST PASSED")
