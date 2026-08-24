from unittest.mock import patch

from app.schemas.evidence import Evidence
from app.services.ship30_generation_service import (
    generate_ship30_plan,
)


EVIDENCE = [
    Evidence(
        evidence_id="lauryn-source-21",
        source_id="lauryn-source",
        guest="Lauryn Isford",
        title="Mastering onboarding",
        content=(
            "We rebuilt onboarding and focused on activation "
            "so users could experience value quickly."
        ),
        chunk_index=21,
    )
]


VALID_RESPONSE = """
{
  "goal": "Improve onboarding activation",
  "principles": [
    "Help users experience value quickly."
  ],
  "days_1_7": {
    "actions": [
      {
        "action": "Test the onboarding flow with users.",
        "evidence_ids": ["lauryn-source-21"]
      }
    ]
  },
  "days_8_14": {
    "actions": []
  },
  "days_15_21": {
    "actions": []
  },
  "days_22_30": {
    "actions": []
  },
  "success": [
    "Users experience value more quickly during onboarding."
  ]
}
""".strip()


def test_valid_generation():
    with patch(
        "app.services.ship30_generation_service.generate_response",
        return_value=VALID_RESPONSE,
    ):
        plan = generate_ship30_plan(
            question="How can we improve onboarding?",
            evidence=EVIDENCE,
        )

    assert plan.goal == "Improve onboarding activation"

    assert len(plan.days_1_7.actions) == 1

    action = plan.days_1_7.actions[0]

    assert action.evidence_ids == [
        "lauryn-source-21"
    ]

    assert plan.days_8_14.actions == []
    assert plan.days_15_21.actions == []
    assert plan.days_22_30.actions == []

    print("VALID GENERATION TEST PASSED")


def test_invalid_json():
    with patch(
        "app.services.ship30_generation_service.generate_response",
        return_value="this is not json",
    ):
        try:
            generate_ship30_plan(
                question="How can we improve onboarding?",
                evidence=EVIDENCE,
            )
        except ValueError:
            print("INVALID JSON TEST PASSED")
            return

    raise AssertionError(
        "Invalid JSON was not rejected."
    )


def test_missing_required_field():
    invalid_response = """
    {
      "goal": "Improve onboarding",
      "principles": [],
      "days_1_7": {
        "actions": []
      }
    }
    """.strip()

    with patch(
        "app.services.ship30_generation_service.generate_response",
        return_value=invalid_response,
    ):
        try:
            generate_ship30_plan(
                question="How can we improve onboarding?",
                evidence=EVIDENCE,
            )
        except Exception:
            print("MISSING FIELD TEST PASSED")
            return

    raise AssertionError(
        "Missing required fields were not rejected."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("SHIP30 GENERATION TESTS")
    print("=" * 70)

    test_valid_generation()
    test_invalid_json()
    test_missing_required_field()

    print()
    print("ALL GENERATION TESTS PASSED")
