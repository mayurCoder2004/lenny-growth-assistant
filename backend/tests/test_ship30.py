import json

import pytest

from app.services.plan_validation import validate_ship30_plan
from app.services.ship30_generation_service import generate_ship30_plan


def valid_payload(indexes=None):
    return {
        "goal": "Improve activation through clearer onboarding.",
        "principles": [
            "Help users experience product value quickly."
        ],
        "days_1_7": {
            "actions": [
                {
                    "action": (
                        "Improve onboarding so users experience "
                        "product value quickly."
                    ),
                    "evidence_indexes": [0] if indexes is None else indexes,
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
            "Users experience product value quickly."
        ],
    }


def test_ship30_generation_requires_evidence():
    with pytest.raises(ValueError) as exc_info:
        generate_ship30_plan(
            question="How do I improve onboarding?",
            evidence=[],
        )

    assert "without evidence" in str(exc_info.value)


def test_evidence_indexes_are_converted_into_real_evidence_ids(
    monkeypatch,
    sample_evidence,
):
    monkeypatch.setattr(
        "app.services.ship30_generation_service.generate_response",
        lambda **kwargs: json.dumps(valid_payload()),
    )

    plan = generate_ship30_plan(
        question="How do I improve activation onboarding?",
        evidence=sample_evidence,
    )

    action = plan.days_1_7.actions[0]

    assert action.evidence_ids == ["source-1-0"]


def test_invalid_evidence_indexes_are_rejected(
    monkeypatch,
    sample_evidence,
):
    monkeypatch.setattr(
        "app.services.ship30_generation_service.generate_response",
        lambda **kwargs: json.dumps(valid_payload(indexes=[9])),
    )

    with pytest.raises(ValueError) as exc_info:
        generate_ship30_plan(
            question="How do I improve activation onboarding?",
            evidence=sample_evidence,
        )

    assert "invalid evidence index" in str(exc_info.value)


def test_generated_ship30_plan_passes_deterministic_validation(
    monkeypatch,
    sample_evidence,
):
    monkeypatch.setattr(
        "app.services.ship30_generation_service.generate_response",
        lambda **kwargs: json.dumps(valid_payload()),
    )

    plan = generate_ship30_plan(
        question="How do I improve activation onboarding?",
        evidence=sample_evidence,
    )

    assert validate_ship30_plan(plan, sample_evidence) is plan
