from typing import Any


def build_transcript_context(
    results: list[dict[str, Any]],
) -> str:
    """
    Build a compact transcript context for the LLM.

    Only includes information that the LLM needs:
    guest, episode, and transcript excerpt.
    """

    if not results:
        return ""

    context_parts: list[str] = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"""
SOURCE {index}

Guest: {result["guest"]}
Episode: {result["title"]}

Transcript excerpt:
{result["content"]}
""".strip()
        )

    return "\n\n".join(context_parts)
