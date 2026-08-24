from unittest.mock import Mock, patch

from app.schemas.evidence import Evidence
from app.services.ship30_skill_service import (
    Ship30SkillService,
    Ship30SkillServiceError,
)
from app.skills.ship30_skill import Ship30Essay


CANDIDATES = [
    {
        "source_id": "lauryn-source",
        "content": (
            "We rebuilt onboarding and focused on activation, "
            "helping users experience value quickly."
        ),
        "chunk_index": 21,
        "title": "Mastering onboarding",
        "guest": "Lauryn Isford",
        "url": None,
        "distance": 0.50,
    }
]


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


ESSAY = Ship30Essay(
    content=(
        "# Improving Onboarding\n\n"
        "Help users experience value quickly."
    ),
    evidence_ids=[
        "lauryn-source-21",
    ],
)


def test_full_orchestration():
    db = object()

    skill = Mock()

    skill.generate.return_value = ESSAY

    service = Ship30SkillService(
        skill=skill,
    )

    with patch(
        "app.services.ship30_skill_service.search_similar_chunks",
        return_value=CANDIDATES,
    ) as retrieval_mock, patch(
        "app.services.ship30_skill_service.select_grounded_evidence",
        return_value=EVIDENCE,
    ) as grounding_mock:

        result = service.generate(
            db=db,
            question="How can I improve onboarding?",
        )

    assert result is ESSAY

    retrieval_mock.assert_called_once_with(
        db=db,
        query="How can I improve onboarding?",
        limit=20,
        candidate_limit=20,
    )

    grounding_mock.assert_called_once_with(
        question="How can I improve onboarding?",
        candidates=CANDIDATES,
        max_evidence=5,
        distance_threshold=0.60,
    )

    skill.generate.assert_called_once_with(
        question="How can I improve onboarding?",
        evidence=EVIDENCE,
    )

    print("SHIP30 SKILL FULL ORCHESTRATION: PASSED")


def test_no_retrieval_candidates():
    db = object()

    service = Ship30SkillService(
        skill=Mock(),
    )

    with patch(
        "app.services.ship30_skill_service.search_similar_chunks",
        return_value=[],
    ):
        try:
            service.generate(
                db=db,
                question="How can I improve onboarding?",
            )
        except Ship30SkillServiceError as exc:
            assert "No retrieval candidates" in str(exc)
            print("SHIP30 SKILL NO CANDIDATES: PASSED")
            return

    raise AssertionError(
        "Expected Ship30SkillServiceError."
    )


def test_no_grounded_evidence():
    db = object()

    service = Ship30SkillService(
        skill=Mock(),
    )

    with patch(
        "app.services.ship30_skill_service.search_similar_chunks",
        return_value=CANDIDATES,
    ), patch(
        "app.services.ship30_skill_service.select_grounded_evidence",
        return_value=[],
    ):
        try:
            service.generate(
                db=db,
                question="How can I improve onboarding?",
            )
        except Ship30SkillServiceError as exc:
            assert "No sufficiently relevant evidence" in str(exc)
            print("SHIP30 SKILL NO GROUNDED EVIDENCE: PASSED")
            return

    raise AssertionError(
        "Expected Ship30SkillServiceError."
    )


def test_empty_question():
    service = Ship30SkillService(
        skill=Mock(),
    )

    try:
        service.generate(
            db=object(),
            question="",
        )
    except Ship30SkillServiceError as exc:
        assert "Question cannot be empty" in str(exc)
        print("SHIP30 SKILL EMPTY QUESTION: PASSED")
        return

    raise AssertionError(
        "Expected Ship30SkillServiceError."
    )


def test_database_required():
    service = Ship30SkillService(
        skill=Mock(),
    )

    try:
        service.generate(
            db=None,
            question="How can I improve onboarding?",
        )
    except Ship30SkillServiceError as exc:
        assert "database session is required" in str(exc)
        print("SHIP30 SKILL DATABASE REQUIREMENT: PASSED")
        return

    raise AssertionError(
        "Expected Ship30SkillServiceError."
    )


def test_skill_error_is_wrapped():
    db = object()

    skill = Mock()

    skill.generate.side_effect = Exception(
        "LLM unavailable"
    )

    service = Ship30SkillService(
        skill=skill,
    )

    with patch(
        "app.services.ship30_skill_service.search_similar_chunks",
        return_value=CANDIDATES,
    ), patch(
        "app.services.ship30_skill_service.select_grounded_evidence",
        return_value=EVIDENCE,
    ):
        try:
            service.generate(
                db=db,
                question="How can I improve onboarding?",
            )
        except Ship30SkillServiceError as exc:
            assert "Failed to generate Ship30 essay" in str(exc)
            assert "LLM unavailable" in str(exc)
            print("SHIP30 SKILL ERROR HANDLING: PASSED")
            return

    raise AssertionError(
        "Expected Ship30SkillServiceError."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 8 SHIP30 SKILL SERVICE TESTS")
    print("=" * 70)

    test_full_orchestration()
    test_no_retrieval_candidates()
    test_no_grounded_evidence()
    test_empty_question()
    test_database_required()
    test_skill_error_is_wrapped()

    print()
    print("ALL PHASE 8 SHIP30 SKILL SERVICE TESTS PASSED")
