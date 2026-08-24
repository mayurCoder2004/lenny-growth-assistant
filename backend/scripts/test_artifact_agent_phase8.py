from unittest.mock import Mock

from app.agents.artifact_agent import (
    ArtifactAgent,
    ArtifactAgentError,
)
from app.services.ship30_skill_service import (
    Ship30SkillService,
)
from app.skills.ship30_skill import Ship30Essay


ESSAY = Ship30Essay(
    content=(
        "# Improving Onboarding\n\n"
        "Help users experience value quickly."
    ),
    evidence_ids=[
        "lauryn-source-21",
        "itamar-source-28",
    ],
)


def test_artifact_agent_generates_essay():
    service = Mock(spec=Ship30SkillService)

    service.generate.return_value = ESSAY

    agent = ArtifactAgent(
        skill_service=service,
    )

    db = object()

    result = agent.execute(
        db=db,
        message="How can I improve onboarding?",
    )

    assert result["agent"] == "artifact"

    assert result["answer"] == ESSAY.content

    assert result["plan"] is None

    assert result["sources"] == [
        {
            "evidence_id": "lauryn-source-21",
        },
        {
            "evidence_id": "itamar-source-28",
        },
    ]

    service.generate.assert_called_once_with(
        db=db,
        question="How can I improve onboarding?",
    )

    print("ARTIFACT AGENT ESSAY GENERATION: PASSED")


def test_artifact_agent_query_alias():
    service = Mock(spec=Ship30SkillService)

    service.generate.return_value = ESSAY

    agent = ArtifactAgent(
        skill_service=service,
    )

    result = agent.execute(
        db=object(),
        query="How can I improve onboarding?",
    )

    assert result["answer"] == ESSAY.content

    service.generate.assert_called_once_with(
        db=service.generate.call_args.kwargs["db"],
        question="How can I improve onboarding?",
    )

    print("ARTIFACT AGENT QUERY ALIAS: PASSED")


def test_artifact_agent_rejects_empty_message():
    agent = ArtifactAgent(
        skill_service=Mock(),
    )

    try:
        agent.execute(
            db=object(),
            message="",
        )
    except ArtifactAgentError as exc:
        assert "Message cannot be empty" in str(exc)
        print("ARTIFACT AGENT EMPTY MESSAGE: PASSED")
        return

    raise AssertionError(
        "Expected ArtifactAgentError."
    )


def test_artifact_agent_requires_database():
    agent = ArtifactAgent(
        skill_service=Mock(),
    )

    try:
        agent.execute(
            db=None,
            message="How can I improve onboarding?",
        )
    except ArtifactAgentError as exc:
        assert "database session is required" in str(exc)
        print("ARTIFACT AGENT DATABASE REQUIREMENT: PASSED")
        return

    raise AssertionError(
        "Expected ArtifactAgentError."
    )


def test_artifact_agent_wraps_skill_service_error():
    service = Mock(spec=Ship30SkillService)

    service.generate.side_effect = Exception(
        "skill unavailable"
    )

    agent = ArtifactAgent(
        skill_service=service,
    )

    try:
        agent.execute(
            db=object(),
            message="How can I improve onboarding?",
        )
    except ArtifactAgentError as exc:
        assert "Failed to generate artifact" in str(exc)
        assert "skill unavailable" in str(exc)
        print("ARTIFACT AGENT ERROR HANDLING: PASSED")
        return

    raise AssertionError(
        "Expected ArtifactAgentError."
    )


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 8 ARTIFACT AGENT TESTS")
    print("=" * 70)

    test_artifact_agent_generates_essay()
    test_artifact_agent_query_alias()
    test_artifact_agent_rejects_empty_message()
    test_artifact_agent_requires_database()
    test_artifact_agent_wraps_skill_service_error()

    print()
    print("ALL PHASE 8 ARTIFACT AGENT TESTS PASSED")
