import json

from app.schemas.ship30 import Ship30Plan
from app.services.llm_service import generate_response
from app.services.plan_validation import validate_ship30_plan


def _build_evidence_context(evidence) -> str:
    """
    Build explicit evidence context for structured Ship30 generation.
    """

    if not evidence:
        return ""

    parts: list[str] = []

    for item in evidence:
        parts.append(
            f"""
EVIDENCE ID: {item.evidence_id}

Guest: {item.guest}
Episode: {item.title}

Transcript:
{item.content}
""".strip()
        )

    return "\n\n".join(parts)


def _build_prompt(
    question: str,
    evidence,
) -> str:
    """
    Build a structured-generation prompt.

    The model may only reference evidence IDs supplied here.
    """

    context = _build_evidence_context(evidence)

    return f"""
USER QUESTION:

{question}


SELECTED EVIDENCE:

{context}


TASK:

Create a practical 30-day plan answering the user's question.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
  "goal": "string",
  "principles": ["string"],
  "days_1_7": {{
    "actions": [
      {{
        "action": "string",
        "evidence_ids": ["evidence-id"]
      }}
    ]
  }},
  "days_8_14": {{
    "actions": []
  }},
  "days_15_21": {{
    "actions": []
  }},
  "days_22_30": {{
    "actions": []
  }},
  "success": ["string"]
}}


CRITICAL GROUNDING RULES:

1. Every action MUST contain at least one evidence_id.

2. Every evidence_id MUST exactly match an EVIDENCE ID supplied above.

3. NEVER invent an evidence_id.

4. Only create actions directly supported by the supplied transcript
   evidence.

5. Do not create generic advice that is not supported by the evidence.

6. Do not invent numerical targets.

7. If the evidence does not support an action for a particular phase,
   leave that phase's actions empty.

8. Do not create filler actions simply to populate the 30-day plan.

9. Success criteria must also be supported by the evidence.

10. Do not use outside knowledge.

11. Do not mention evidence IDs outside the evidence_ids fields.

12. Do not include markdown fences.

Return ONLY the JSON object.
""".strip()


def _extract_json(response: str) -> dict:
    """
    Parse the model's JSON response.

    Markdown fences are intentionally rejected rather than silently
    changing malformed model output.
    """

    if not response or not response.strip():
        raise ValueError("LLM returned an empty response.")

    text = response.strip()

    if text.startswith("```") or text.endswith("```"):
        raise ValueError(
            "LLM returned markdown instead of raw JSON."
        )

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            "LLM JSON response must be an object."
        )

    return parsed


def generate_ship30_plan(
    question: str,
    evidence,
) -> Ship30Plan:
    """
    Generate a structured Ship30 plan from grounded evidence.

    This function performs:
        Evidence
            ?
        Structured LLM generation
            ?
        JSON parsing
            ?
        Pydantic validation
    """

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not evidence:
        raise ValueError(
            "Cannot generate a Ship30 plan without evidence."
        )

    prompt = _build_prompt(
        question=question.strip(),
        evidence=evidence,
    )

    response = generate_response(
        prompt=prompt,
    )

    payload = _extract_json(response)

    plan = Ship30Plan.model_validate(payload)

    validate_ship30_plan(
        plan=plan,
        evidence=evidence,
    )

    return plan
