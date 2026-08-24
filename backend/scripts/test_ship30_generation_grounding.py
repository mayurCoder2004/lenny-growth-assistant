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
            "We rebuilt onboarding and focused on activation, "
            "helping users experience value quickly."
        ),
        chunk_index=21,
    )
]


INVALID_GROUNDING_RESPONSE = """
{
  "goal": "Improve onboarding activation",
  "principles": [
    "Help users experience value quickly."
  ],
  "days_1_7": {
    "actions": [
      {
        "action": "Test the onboarding flow with users.",
        "evidence_ids": ["fake-evidence-id"]
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
    "Users experience value more quickly."
  ]
}
""".strip()


def test_fake_evidence_id_is_rejected():
    with patch(
        "app.services.ship30_generation_service.generate_response",
        return_value=INVALID_GROUNDING_RESPONSE,
    ):
        try:
            generate_ship30_plan(
                question="How can we improve onboarding?",
                evidence=EVIDENCE,
            )
        except ValueError as exc:
            print("FAKE EVIDENCE ID REJECTION: PASSED")
            print(f"  {exc}")
            return

    raise AssertionError(
        "Fake evidence ID was not rejected."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("SHIP30 GENERATION + GROUNDING INTEGRATION TEST")
    print("=" * 70)

    test_fake_evidence_id_is_rejected()

    print()
    print("INTEGRATION TEST PASSED")
