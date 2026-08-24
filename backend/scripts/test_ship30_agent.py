from unittest.mock import patch

from app.schemas.ship30 import (
    PlanAction,
    PlanPhase,
    Ship30Plan,
)
from app.agents.ship30_agent import (
    Ship30Agent,
    Ship30AgentError,
)


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


def test_agent_execute():
    agent = Ship30Agent()
    db = object()

    with patch(
        "app.agents.ship30_agent.generate_ship30",
        return_value=PLAN,
    ) as generate_mock:

        result = agent.execute(
            db=db,
            message="How can I improve onboarding?",
        )

    assert result["agent"] == "ship30"
    assert result["plan"] == PLAN

    assert "Improve onboarding activation" in result["answer"]

    assert result["sources"] == [
        {
            "evidence_id": "source-1-21",
        }
    ]

    generate_mock.assert_called_once_with(
        db=db,
        question="How can I improve onboarding?",
        candidate_limit=20,
        max_evidence=5,
        distance_threshold=0.60,
    )

    print("AGENT EXECUTE: PASSED")


def test_agent_query_alias():
    agent = Ship30Agent()

    with patch(
        "app.agents.ship30_agent.generate_ship30",
        return_value=PLAN,
    ) as generate_mock:

        result = agent.execute(
            db=object(),
            query="How can I improve onboarding?",
        )

    assert result["agent"] == "ship30"
    assert result["plan"] == PLAN

    assert generate_mock.call_args.kwargs["question"] == (
        "How can I improve onboarding?"
    )

    print("QUERY ALIAS: PASSED")


def test_agent_empty_message():
    agent = Ship30Agent()

    try:
        agent.execute(
            db=object(),
            message="   ",
        )
    except Ship30AgentError as exc:
        assert "Message cannot be empty" in str(exc)
        print("EMPTY MESSAGE: PASSED")
        return

    raise AssertionError(
        "Expected Ship30AgentError for empty message."
    )


def test_agent_requires_database():
    agent = Ship30Agent()

    try:
        agent.execute(
            message="How can I improve onboarding?",
        )
    except Ship30AgentError as exc:
        assert "database session is required" in str(exc)
        print("DATABASE REQUIREMENT: PASSED")
        return

    raise AssertionError(
        "Expected Ship30AgentError when db is missing."
    )


def test_run_and_generate():
    agent = Ship30Agent()

    with patch(
        "app.agents.ship30_agent.generate_ship30",
        return_value=PLAN,
    ) as generate_mock:

        result = agent.run(
            query="How can I improve onboarding?",
            db=object(),
        )

        assert result == PLAN

        result = agent.generate(
            query="How can I improve onboarding?",
            db=object(),
        )

    assert result == PLAN
    assert generate_mock.call_count == 2

    print("RUN + GENERATE: PASSED")


if __name__ == "__main__":
    print("=" * 70)
    print("SHIP30 AGENT TESTS")
    print("=" * 70)

    test_agent_execute()
    test_agent_query_alias()
    test_agent_empty_message()
    test_agent_requires_database()
    test_run_and_generate()

    print()
    print("ALL SHIP30 AGENT TESTS PASSED")
