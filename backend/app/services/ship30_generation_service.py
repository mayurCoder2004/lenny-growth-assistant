import json

from app.schemas.ship30 import Ship30Plan
from app.services.llm_service import generate_response
from app.services.plan_validation import validate_ship30_plan


def _build_evidence_context(evidence) -> str:
    """
    Build explicit evidence context using stable integer indexes.

    The LLM sees indexes only. Backend evidence IDs remain internal.
    """

    if not evidence:
        return ""

    parts: list[str] = []

    for index, item in enumerate(evidence):
        parts.append(
            f"""
EVIDENCE INDEX: {index}

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

    The model may only reference evidence indexes supplied here.
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
        "evidence_indexes": [0]
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


CRITICAL ACTION GENERATION RULE:

Before creating an action, compare the action wording directly against
the selected transcript.

An action is valid ONLY when the transcript explicitly contains the
idea, behavior, strategy, or recommendation described by the action.

Prefer short actions that reuse the transcript's own terminology.

Do NOT expand, reinterpret, or generalize transcript ideas into new
activities.

When only one or two actions are directly supported by the evidence,
create only those actions. It is completely valid for other phases
to contain no actions.
CRITICAL GROUNDING RULES:

1. Every action MUST contain at least one evidence_index.

2. Every evidence_index MUST be an integer referring to an EVIDENCE INDEX supplied above.

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


def _resolve_evidence_indexes(
    payload: dict,
    evidence,
) -> dict:
    """
    Convert LLM evidence indexes into real backend evidence IDs.
    """

    normalized = dict(payload)

    evidence_by_index = {
        index: item.evidence_id
        for index, item in enumerate(evidence)
    }

    phases = (
        "days_1_7",
        "days_8_14",
        "days_15_21",
        "days_22_30",
    )

    for phase_name in phases:
        phase = normalized.get(phase_name)

        if not isinstance(phase, dict):
            continue

        actions = phase.get("actions", [])

        if not isinstance(actions, list):
            continue

        for action in actions:
            if not isinstance(action, dict):
                continue

            indexes = action.pop("evidence_indexes", None)

            if indexes is None:
                raise ValueError(
                    f"{phase_name} action is missing evidence_indexes."
                )

            if not isinstance(indexes, list) or not indexes:
                raise ValueError(
                    f"{phase_name} action must contain evidence indexes."
                )

            resolved_ids = []

            for index in indexes:
                if isinstance(index, bool) or not isinstance(index, int):
                    raise ValueError(
                        f"{phase_name} contains invalid evidence index: {index}"
                    )

                if index not in evidence_by_index:
                    raise ValueError(
                        f"{phase_name} references invalid evidence index: {index}"
                    )

                resolved_ids.append(
                    evidence_by_index[index]
                )

            action["evidence_ids"] = resolved_ids

    return normalized

def generate_ship30_plan(
    question: str,
    evidence,
) -> Ship30Plan:
    """
    Generate a structured Ship30 plan from grounded evidence.
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

    # Normalize simple LLM formatting differences.
    payload = dict(payload)

    if isinstance(payload.get("success"), str):
        payload["success"] = [
            payload["success"]
        ]

    # Convert LLM evidence indexes into real backend evidence IDs.
    payload = _resolve_evidence_indexes(
        payload=payload,
        evidence=evidence,
    )

    plan = Ship30Plan.model_validate(
        payload
    )

    validate_ship30_plan(
        plan=plan,
        evidence=evidence,
    )

    return plan


