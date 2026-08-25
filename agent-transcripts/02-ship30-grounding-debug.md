# Ship30 Grounding Debug Transcript

## Failure

The structured Ship30 plan pipeline originally had a mismatch between what the LLM generated and what the backend schema expected.

The LLM generated fields like:

```json
{
  "action": "Focus onboarding around helping users experience value quickly.",
  "evidence_indexes": [0]
}
```

The Pydantic schema in `backend/app/schemas/ship30.py` expected:

```json
{
  "action": "Focus onboarding around helping users experience value quickly.",
  "evidence_ids": ["real-source-id-21"]
}
```

This caused validation failures because the model was not returning `evidence_ids`.

## Root Cause

Backend evidence IDs are deterministic but long and easy for a small local model to copy incorrectly. Asking the LLM to produce exact backend IDs created unnecessary structured-output fragility.

## Fix

`backend/app/services/ship30_generation_service.py` now exposes integer evidence indexes to the LLM. The prompt instructs the model to return `evidence_indexes`.

After JSON parsing, `_resolve_evidence_indexes()` maps each integer index back to the real selected `Evidence.evidence_id`, writes `evidence_ids`, and removes `evidence_indexes`.

Validation then occurs after resolution:

1. `_extract_json()`
2. `_resolve_evidence_indexes()`
3. `Ship30Plan.model_validate()`
4. `validate_ship30_plan()`

## Result

The LLM gets a simpler reference format, while the backend still validates every final action against real selected evidence IDs.
