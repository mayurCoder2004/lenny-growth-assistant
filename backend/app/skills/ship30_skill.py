from __future__ import annotations

from dataclasses import dataclass

from app.schemas.evidence import Evidence
from app.services.llm_service import generate_response


class Ship30SkillError(Exception):
    """Raised when Ship30 essay generation fails."""


@dataclass(frozen=True)
class Ship30Essay:
    """Generated Ship30-style essay with its supporting evidence."""

    content: str
    evidence_ids: list[str]


class Ship30Skill:
    """
    Generate transcript-grounded Ship30-style essays.

    Retrieval and evidence selection happen outside the skill.
    This class is responsible only for transforming selected evidence
    into a Ship30-style written artifact.
    """

    def generate(
        self,
        question: str,
        evidence: list[Evidence],
    ) -> Ship30Essay:
        if not question or not question.strip():
            raise Ship30SkillError(
                "Question cannot be empty."
            )

        if not evidence:
            raise Ship30SkillError(
                "Evidence is required."
            )

        prompt = self._build_prompt(
            question=question.strip(),
            evidence=evidence,
        )

        try:
            response = generate_response(
                prompt=prompt,
                system_prompt=self._system_prompt(),
            )
        except Exception as exc:
            raise Ship30SkillError(
                f"Failed to generate Ship30 essay: {exc}"
            ) from exc

        essay = response.strip()

        if not essay:
            raise Ship30SkillError(
                "LLM returned an empty essay."
            )

        return Ship30Essay(
            content=essay,
            evidence_ids=[
                item.evidence_id
                for item in evidence
            ],
        )

    def _build_prompt(
        self,
        question: str,
        evidence: list[Evidence],
    ) -> str:
        context_parts: list[str] = []

        for item in evidence:
            context_parts.append(
                f"""
EVIDENCE ID: {item.evidence_id}

Guest: {item.guest or "Unknown"}
Episode: {item.title or "Unknown"}

Transcript:
{item.content[:3500]}
""".strip()
            )

        context = "\n\n".join(context_parts)

        return f"""
USER REQUEST:

{question}


SELECTED TRANSCRIPT EVIDENCE:

{context}


TASK:

Write a Ship 30-style essay that answers the user's request.


SHIP 30 WRITING PRINCIPLES:

1. Start with a strong, specific hook.

2. Build the essay around one central idea.

3. Create a clear narrative progression from the opening
   to the final takeaway.

4. Use short, readable paragraphs.

5. Use headings when they improve readability.

6. Use selective bold emphasis for important ideas.

7. Include concrete examples only when supported by the
   supplied transcript evidence.

8. End with a useful practical takeaway.

9. Aim for approximately 700 words.

10. Every substantive factual claim must be grounded in the
    supplied transcript evidence.

11. Do not invent facts, examples, quotes, statistics,
    experiences, or recommendations.

12. Do not use outside knowledge.

13. Do not fabricate quotations. Paraphrase transcript
    material unless an exact quote is explicitly supported.

14. Do not mention evidence IDs in the essay.

15. Do not discuss retrieval, embeddings, prompts,
    vector databases, or internal system behavior.

16. If the evidence does not adequately support the requested
    essay, clearly state that the available transcript evidence
    is insufficient rather than inventing material.

Return only the essay.
""".strip()

    def _system_prompt(self) -> str:
        return """
You are the Ship 30 writing skill for Lenny Growth Assistant.

Your job is to transform selected Lenny's Podcast transcript evidence
into a useful, readable Ship 30-style essay.

The supplied evidence is the only factual source you may use.

Ground every substantive claim in that evidence.

Never invent facts, examples, statistics, quotes, or outside knowledge.

Preserve the meaning of the original speakers.

Do not force unrelated evidence into the essay.

Write naturally and clearly.

The final essay should have a strong hook, one central idea,
narrative progression, short paragraphs, useful headings,
selective emphasis, concrete evidence-supported examples,
and a practical takeaway.

Aim for approximately 700 words.
""".strip()

