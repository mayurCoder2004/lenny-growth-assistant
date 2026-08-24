from unittest.mock import patch

from app.schemas.evidence import Evidence
from app.schemas.ship30 import (
    PlanAction,
    PlanPhase,
    Ship30Plan,
)
from app.services.ship30_service import (
    Ship30ServiceError,
    generate_ship30,
)


CANDIDATES = [
    {
        "id": "chunk-1",
        "source_id": "source-1",
        "content": (
            "We rebuilt onboarding and focused on activation, "
            "helping users experience value quickly."
        ),
        "chunk_index": 21,
        "title": "Mastering onboarding",
        "guest": "Lauryn Isford",
        "url": None,
        "published_at": None,
        "distance": 0.45,
    }
]


EVIDENCE = [
    Evidence(
        evidence_id="source-1-21",
        source_id="source-1",
        guest="Lauryn Isford",
        title="Mastering onboarding",
        content=(
            "We rebuilt onboarding and focused on activation, "
            "helping users experience value quickly."
        ),
        chunk_index=21,
    )
]


PLAN = Ship30Plan(
    goal="Improve onboarding activation",
    principles=[
        "Help users experience value quickly."
    ],
    days_1_7=PlanPhase(
        actions=[
            PlanAction(
                action=(
                    "Improve onboarding so users experience "
                    "value quickly."
                ),
                evidence_ids=["source-1-21"],
            )
        ]
    ),
    days_8_14=PlanPhase(actions=[]),
    days_15_21=PlanPhase(actions=[]),
    days_22_30=PlanPhase(actions=[]),
    success=[
        "Users experience value more quickly."
    ],
)


def test_full_orchestration():
    with patch(
        "app.services.ship30_service.search_similar_chunks",
        return_value=CANDIDATES,
    ) as retrieval_mock, patch(
        "app.services.ship30_service.select_grounded_evidence",
        return_value=EVIDENCE,
    ) as grounding_mock, patch(
        "app.services.ship30_service.generate_ship30_plan",
        return_value=PLAN,
    ) as generation_mock:

        result = generate_ship30(
            db=None,
            question="How can we improve onboarding?",
        )

    assert result == PLAN

    retrieval_mock.assert_called_once()

    grounding_mock.assert_called_once_with(
        question="How can we improve onboarding?",
        candidates=CANDIDATES,
        max_evidence=5,
        distance_threshold=0.60,
    )

    generation_mock.assert_called_once_with(
        question="How can we improve onboarding?",
        evidence=EVIDENCE,
    )

    print("FULL ORCHESTRATION: PASSED")


def test_no_candidates():
    with patch(
        "app.services.ship30_service.search_similar_chunks",
        return_value=[],
    ):
        try:
            generate_ship30(
                db=None,
                question="How can we improve onboarding?",
            )
        except Ship30ServiceError as exc:
            assert "No retrieval candidates" in str(exc)
            print("NO CANDIDATES: PASSED")
            return

    raise AssertionError(
        "Expected Ship30ServiceError for empty retrieval."
    )


def test_no_grounded_evidence():
    with patch(
        "app.services.ship30_service.search_similar_chunks",
        return_value=CANDIDATES,
    ), patch(
        "app.services.ship30_service.select_grounded_evidence",
        return_value=[],
    ):
        try:
            generate_ship30(
                db=None,
                question="How can we improve onboarding?",
            )
        except Ship30ServiceError as exc:
            assert "No sufficiently relevant evidence" in str(exc)
            print("NO GROUNDED EVIDENCE: PASSED")
            return

    raise AssertionError(
        "Expected Ship30ServiceError for empty evidence."
    )


def test_empty_question():
    try:
        generate_ship30(
            db=None,
            question="   ",
        )
    except Ship30ServiceError as exc:
        assert "Question cannot be empty" in str(exc)
        print("EMPTY QUESTION: PASSED")
        return

    raise AssertionError(
        "Expected Ship30ServiceError for empty question."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("SHIP30 SERVICE ORCHESTRATION TESTS")
    print("=" * 70)

    test_full_orchestration()
    test_no_candidates()
    test_no_grounded_evidence()
    test_empty_question()

    print()
    print("ALL SHIP30 SERVICE TESTS PASSED")
