import re
from typing import Iterable

from app.schemas.evidence import Evidence
from app.schemas.ship30 import PlanAction, Ship30Plan


GENERIC_ACTION_PATTERNS = [
    r"\bconduct user research\b",
    r"\bdo user research\b",
    r"\bimplement a pilot\b",
    r"\brun a pilot\b",
    r"\bgather feedback\b",
    r"\bcollect feedback\b",
    r"\bimprove the product\b",
    r"\bcreate a roadmap\b",
    r"\bbuild a roadmap\b",
    r"\bmeasure progress\b",
    r"\bmonitor progress\b",
    r"\bmonitor user satisfaction\b",
]


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "can", "do", "does", "for", "from", "how", "i",
    "in", "is", "it", "me", "of", "on", "or", "should",
    "that", "the", "their", "this", "to", "was", "what",
    "when", "where", "which", "who", "why", "with",
    "you", "your",
}


def _normalize(text: str) -> str:
    """
    Normalize text for deterministic comparison.
    """
    return re.sub(
        r"[^a-z0-9%.\s]",
        " ",
        text.lower(),
    )


def _tokens(text: str) -> set[str]:
    """
    Extract meaningful tokens.
    """
    return {
        token
        for token in _normalize(text).split()
        if (
            token
            and token not in STOP_WORDS
            and len(token) > 2
        )
    }


def _numbers(text: str) -> set[str]:
    """
    Extract numerical claims.

    Supports:
    - integers
    - decimals
    - percentages
    - simple multipliers such as 2x
    """
    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?(?:%|x)?\b",
            text.lower(),
        )
    )


def _supported_numbers(
    text: str,
    evidence_text: str,
) -> bool:
    """
    Return True when every numerical claim in text
    is supported somewhere in the evidence.
    """
    claimed_numbers = _numbers(text)

    if not claimed_numbers:
        return True

    evidence_numbers = _numbers(evidence_text)

    return claimed_numbers.issubset(
        evidence_numbers
    )


def _lexical_support(
    text: str,
    evidence_text: str,
) -> float:
    """
    Measure meaningful lexical overlap between an action
    and its supporting evidence.
    """
    text_tokens = _tokens(text)
    evidence_tokens = _tokens(evidence_text)

    if not text_tokens:
        return 0.0

    return len(
        text_tokens & evidence_tokens
    ) / len(text_tokens)


def _contains_generic_action(text: str) -> bool:
    """
    Detect generic actions explicitly prohibited by Phase 6.
    """
    normalized = _normalize(text)

    return any(
        re.search(pattern, normalized)
        for pattern in GENERIC_ACTION_PATTERNS
    )


def _evidence_map(
    evidence: Iterable[Evidence],
) -> dict[str, Evidence]:
    """
    Build an evidence lookup by stable evidence ID.
    """
    return {
        item.evidence_id: item
        for item in evidence
    }


def _action_evidence_text(
    action: PlanAction,
    evidence_by_id: dict[str, Evidence],
) -> str:
    """
    Combine the transcript text referenced by an action.
    """
    return "\n\n".join(
        evidence_by_id[evidence_id].content
        for evidence_id in action.evidence_ids
        if evidence_id in evidence_by_id
    )


def validate_evidence_references(
    plan: Ship30Plan,
    evidence: list[Evidence],
) -> None:
    """
    Ensure every action references real selected evidence IDs.
    """
    evidence_by_id = _evidence_map(evidence)

    for phase_name in (
        "days_1_7",
        "days_8_14",
        "days_15_21",
        "days_22_30",
    ):
        phase = getattr(plan, phase_name)

        for action in phase.actions:
            if not action.evidence_ids:
                raise ValueError(
                    f"{phase_name} contains an action without evidence_ids."
                )

            invalid_ids = [
                evidence_id
                for evidence_id in action.evidence_ids
                if evidence_id not in evidence_by_id
            ]

            if invalid_ids:
                raise ValueError(
                    f"{phase_name} action references invalid evidence IDs: "
                    f"{invalid_ids}"
                )


def validate_numerical_claims(
    plan: Ship30Plan,
    evidence: list[Evidence],
) -> None:
    """
    Reject numerical claims that do not occur in the referenced evidence.
    """
    evidence_by_id = _evidence_map(evidence)

    for phase_name in (
        "days_1_7",
        "days_8_14",
        "days_15_21",
        "days_22_30",
    ):
        phase = getattr(plan, phase_name)

        for action in phase.actions:
            evidence_text = _action_evidence_text(
                action,
                evidence_by_id,
            )

            if not _supported_numbers(
                action.action,
                evidence_text,
            ):
                raise ValueError(
                    f"{phase_name} contains an unsupported numerical "
                    f"claim: {action.action}"
                )


def validate_actions(
    plan: Ship30Plan,
    evidence: list[Evidence],
    minimum_lexical_support: float = 0.15,
) -> None:
    """
    Validate that actions are actually supported by their referenced
    transcript evidence.

    This is intentionally conservative but not based on exact sentence
    matching. The evidence IDs provide the hard grounding boundary,
    while lexical overlap provides a deterministic support check.
    """
    evidence_by_id = _evidence_map(evidence)

    for phase_name in (
        "days_1_7",
        "days_8_14",
        "days_15_21",
        "days_22_30",
    ):
        phase = getattr(plan, phase_name)

        for action in phase.actions:
            if _contains_generic_action(action.action):
                raise ValueError(
                    f"{phase_name} contains an unsupported generic action: "
                    f"{action.action}"
                )

            evidence_text = _action_evidence_text(
                action,
                evidence_by_id,
            )

            support = _lexical_support(
                action.action,
                evidence_text,
            )

            if support < minimum_lexical_support:
                raise ValueError(
                    f"{phase_name} action is not sufficiently supported "
                    f"by its referenced evidence: {action.action}"
                )


def validate_success_criteria(
    plan: Ship30Plan,
    evidence: list[Evidence],
    minimum_lexical_support: float = 0.10,
) -> None:
    """
    Validate numerical claims and basic evidence support in success
    criteria.

    Success criteria do not have evidence_ids in the current schema,
    so they are checked against all selected evidence.
    """
    evidence_text = "\n\n".join(
        item.content
        for item in evidence
    )

    for criterion in plan.success:
        if not _supported_numbers(
            criterion,
            evidence_text,
        ):
            raise ValueError(
                f"Success criterion contains an unsupported numerical "
                f"claim: {criterion}"
            )

        if criterion.strip():
            support = _lexical_support(
                criterion,
                evidence_text,
            )

            if support < minimum_lexical_support:
                raise ValueError(
                    f"Success criterion is not sufficiently supported "
                    f"by selected evidence: {criterion}"
                )


def validate_ship30_plan(
    plan: Ship30Plan,
    evidence: list[Evidence],
) -> Ship30Plan:
    """
    Run all post-generation Ship30 grounding validations.

    Validation order:

        Pydantic schema
            ?
        Evidence references
            ?
        Numerical claims
            ?
        Actions
            ?
        Success criteria
            ?
        Validated plan
    """
    if not evidence:
        raise ValueError(
            "Cannot validate a Ship30 plan without evidence."
        )

    validate_evidence_references(
        plan=plan,
        evidence=evidence,
    )

    validate_numerical_claims(
        plan=plan,
        evidence=evidence,
    )

    validate_actions(
        plan=plan,
        evidence=evidence,
    )

    validate_success_criteria(
        plan=plan,
        evidence=evidence,
    )

    return plan
