from app.schemas.evidence import Evidence
from app.schemas.ship30 import (
    PlanAction,
    PlanPhase,
    Ship30Plan,
)
from app.services.plan_validation import (
    validate_ship30_plan,
)


EVIDENCE = [
    Evidence(
        evidence_id="lauryn-source-21",
        source_id="lauryn-source",
        guest="Lauryn Isford",
        title="Mastering onboarding",
        content=(
            "We rebuilt onboarding and focused on activation, "
            "helping users experience value quickly. "
            "We tested the onboarding flow with users before "
            "expanding the implementation."
        ),
        chunk_index=21,
    )
]


def make_plan(action, evidence_ids, success=None):
    return Ship30Plan(
        goal="Improve onboarding activation",
        principles=[
            "Help users experience value quickly."
        ],
        days_1_7=PlanPhase(
            actions=[
                PlanAction(
                    action=action,
                    evidence_ids=evidence_ids,
                )
            ]
        ),
        days_8_14=PlanPhase(actions=[]),
        days_15_21=PlanPhase(actions=[]),
        days_22_30=PlanPhase(actions=[]),
        success=(
            success
            if success is not None
            else [
                "Users experience value more quickly."
            ]
        ),
    )


def expect_rejection(name, plan):
    try:
        validate_ship30_plan(
            plan=plan,
            evidence=EVIDENCE,
        )
    except ValueError as exc:
        print(f"{name}: PASSED")
        print(f"  {exc}")
        return

    raise AssertionError(
        f"{name}: expected validation failure."
    )


def test_valid_plan():
    plan = make_plan(
        action=(
            "Test the onboarding flow with users "
            "to improve activation."
        ),
        evidence_ids=["lauryn-source-21"],
    )

    validate_ship30_plan(
        plan=plan,
        evidence=EVIDENCE,
    )

    print("VALID PLAN: PASSED")


def test_invalid_evidence_id():
    plan = make_plan(
        action="Test the onboarding flow with users.",
        evidence_ids=["fake-evidence-id"],
    )

    expect_rejection(
        "INVALID EVIDENCE ID",
        plan,
    )


def test_fabricated_number():
    plan = make_plan(
        action=(
            "Reach 80% activation by improving onboarding."
        ),
        evidence_ids=["lauryn-source-21"],
    )

    expect_rejection(
        "FABRICATED NUMBER",
        plan,
    )


def test_generic_action():
    plan = make_plan(
        action="Conduct user research.",
        evidence_ids=["lauryn-source-21"],
    )

    expect_rejection(
        "GENERIC ACTION",
        plan,
    )


def test_unsupported_action():
    plan = make_plan(
        action=(
            "Launch a completely new pricing strategy "
            "for enterprise customers."
        ),
        evidence_ids=["lauryn-source-21"],
    )

    expect_rejection(
        "UNSUPPORTED ACTION",
        plan,
    )


def test_empty_phases_allowed():
    plan = make_plan(
        action="Test the onboarding flow with users.",
        evidence_ids=["lauryn-source-21"],
    )

    validate_ship30_plan(
        plan=plan,
        evidence=EVIDENCE,
    )

    assert plan.days_8_14.actions == []
    assert plan.days_15_21.actions == []
    assert plan.days_22_30.actions == []

    print("EMPTY PHASES: PASSED")


def test_unsupported_success_number():
    plan = make_plan(
        action="Test the onboarding flow with users.",
        evidence_ids=["lauryn-source-21"],
        success=[
            "Reach 95% activation."
        ],
    )

    expect_rejection(
        "UNSUPPORTED SUCCESS NUMBER",
        plan,
    )


if __name__ == "__main__":
    print("=" * 70)
    print("SHIP30 PLAN VALIDATION TESTS")
    print("=" * 70)

    test_valid_plan()
    test_invalid_evidence_id()
    test_fabricated_number()
    test_generic_action()
    test_unsupported_action()
    test_empty_phases_allowed()
    test_unsupported_success_number()

    print()
    print("ALL PLAN VALIDATION TESTS PASSED")
