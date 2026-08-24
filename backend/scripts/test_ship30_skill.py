from unittest.mock import patch

from app.schemas.evidence import Evidence
from app.skills.ship30_skill import (
    Ship30Essay,
    Ship30Skill,
    Ship30SkillError,
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
    ),
    Evidence(
        evidence_id="itamar-source-28",
        source_id="itamar-source",
        guest="Itamar Gilad",
        title="Becoming evidence-guided",
        content=(
            "Teams should use evidence to decide what to build "
            "instead of relying on assumptions."
        ),
        chunk_index=28,
    ),
]


VALID_ESSAY = """
# The Fastest Way to Improve Onboarding

Users do not get value from a product because the product exists.
They get value when the onboarding experience helps them reach that
value quickly.

Lauryn Isford described rebuilding onboarding around activation
so users could experience value quickly. That provides a clear
starting point: onboarding should help users reach meaningful
product value as early as possible.

But improving onboarding should not become a collection of guesses.
Itamar Gilad emphasized using evidence to decide what to build
instead of relying on assumptions.

The practical lesson is simple: focus onboarding improvements on
helping users reach value quickly, then use evidence to guide what
you change next.

## The takeaway

Improve the path to value, and let evidence guide the changes.
""".strip()


def test_skill_generates_essay():
    skill = Ship30Skill()

    with patch(
        "app.skills.ship30_skill.generate_response",
        return_value=VALID_ESSAY,
    ) as generate_mock:

        result = skill.generate(
            question="How can I improve onboarding?",
            evidence=EVIDENCE,
        )

    assert isinstance(result, Ship30Essay)

    assert result.content == VALID_ESSAY

    assert result.evidence_ids == [
        "lauryn-source-21",
        "itamar-source-28",
    ]

    generate_mock.assert_called_once()

    call = generate_mock.call_args

    assert "How can I improve onboarding?" in call.kwargs["prompt"]
    assert "lauryn-source-21" in call.kwargs["prompt"]
    assert "itamar-source-28" in call.kwargs["prompt"]

    print("SHIP30 SKILL GENERATION: PASSED")


def test_skill_rejects_empty_question():
    skill = Ship30Skill()

    try:
        skill.generate(
            question="",
            evidence=EVIDENCE,
        )
    except Ship30SkillError as exc:
        assert "Question cannot be empty" in str(exc)
        print("SHIP30 SKILL EMPTY QUESTION: PASSED")
        return

    raise AssertionError(
        "Expected Ship30SkillError."
    )


def test_skill_rejects_missing_evidence():
    skill = Ship30Skill()

    try:
        skill.generate(
            question="How can I improve onboarding?",
            evidence=[],
        )
    except Ship30SkillError as exc:
        assert "Evidence is required" in str(exc)
        print("SHIP30 SKILL MISSING EVIDENCE: PASSED")
        return

    raise AssertionError(
        "Expected Ship30SkillError."
    )


def test_skill_rejects_empty_llm_response():
    skill = Ship30Skill()

    with patch(
        "app.skills.ship30_skill.generate_response",
        return_value="",
    ):
        try:
            skill.generate(
                question="How can I improve onboarding?",
                evidence=EVIDENCE,
            )
        except Ship30SkillError as exc:
            assert "empty essay" in str(exc).lower()
            print("SHIP30 SKILL EMPTY LLM RESPONSE: PASSED")
            return

    raise AssertionError(
        "Expected Ship30SkillError."
    )


def test_skill_wraps_llm_failure():
    skill = Ship30Skill()

    with patch(
        "app.skills.ship30_skill.generate_response",
        side_effect=RuntimeError("provider unavailable"),
    ):
        try:
            skill.generate(
                question="How can I improve onboarding?",
                evidence=EVIDENCE,
            )
        except Ship30SkillError as exc:
            assert "Failed to generate Ship30 essay" in str(exc)
            assert "provider unavailable" in str(exc)
            print("SHIP30 SKILL LLM FAILURE: PASSED")
            return

    raise AssertionError(
        "Expected Ship30SkillError."
    )


def test_prompt_contains_grounding_rules():
    skill = Ship30Skill()

    prompt = skill._build_prompt(
        question="How can I improve onboarding?",
        evidence=EVIDENCE,
    )

    assert "SELECTED TRANSCRIPT EVIDENCE" in prompt
    assert "lauryn-source-21" in prompt
    assert "itamar-source-28" in prompt

    assert "Do not invent facts" in prompt
    assert "Do not use outside knowledge" in prompt
    assert "Do not fabricate quotations" in prompt
    assert "Do not mention evidence IDs" in prompt

    print("SHIP30 SKILL GROUNDING PROMPT: PASSED")


def test_prompt_contains_writing_requirements():
    skill = Ship30Skill()

    prompt = skill._build_prompt(
        question="How can I improve onboarding?",
        evidence=EVIDENCE,
    )

    assert "strong, specific hook" in prompt
    assert "one central idea" in prompt
    assert "narrative progression" in prompt
    assert "short, readable paragraphs" in prompt
    assert "practical takeaway" in prompt
    assert "approximately 1,250 words" in prompt

    print("SHIP30 SKILL WRITING PROMPT: PASSED")


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 8 SHIP30 SKILL TESTS")
    print("=" * 70)

    test_skill_generates_essay()
    test_skill_rejects_empty_question()
    test_skill_rejects_missing_evidence()
    test_skill_rejects_empty_llm_response()
    test_skill_wraps_llm_failure()
    test_prompt_contains_grounding_rules()
    test_prompt_contains_writing_requirements()

    print()
    print("ALL PHASE 8 SHIP30 SKILL TESTS PASSED")
