from typing import Any

from app.schemas.evidence import Evidence


def build_evidence_id(
    source_id: str,
    chunk_index: int | None,
) -> str:
    """
    Build a deterministic ID for a transcript chunk.

    The same source + chunk combination always produces
    the same evidence ID.
    """

    if not source_id or not source_id.strip():
        raise ValueError("source_id cannot be empty.")

    chunk_value = (
        str(chunk_index)
        if chunk_index is not None
        else "unknown"
    )

    return f"{source_id.strip()}-{chunk_value}"


def candidate_to_evidence(
    candidate: dict[str, Any],
) -> Evidence:
    """
    Convert one retrieval candidate into an Evidence object.
    """

    source_id = str(candidate.get("source_id", "")).strip()

    if not source_id:
        raise ValueError(
            "Retrieval candidate is missing source_id."
        )

    content = candidate.get("content")

    if not content or not str(content).strip():
        raise ValueError(
            "Retrieval candidate is missing content."
        )

    chunk_index = candidate.get("chunk_index")

    return Evidence(
        evidence_id=build_evidence_id(
            source_id=source_id,
            chunk_index=chunk_index,
        ),
        source_id=source_id,
        guest=candidate.get("guest"),
        title=candidate.get("title"),
        content=str(content),
        chunk_index=chunk_index,
        url=candidate.get("url"),
        distance=candidate.get("distance"),
    )


def candidates_to_evidence(
    candidates: list[dict[str, Any]],
) -> list[Evidence]:
    """
    Convert retrieval candidates into Evidence objects.

    Duplicate evidence IDs are removed while preserving
    retrieval order.
    """

    evidence: list[Evidence] = []
    seen_ids: set[str] = set()

    for candidate in candidates:
        item = candidate_to_evidence(candidate)

        if item.evidence_id in seen_ids:
            continue

        seen_ids.add(item.evidence_id)
        evidence.append(item)

    return evidence
