# Ship30 Sources Fix Transcript

## Failure

The Ship30 essay pipeline originally returned only evidence IDs from generated essays. That was enough for internal traceability, but it was not enough for the frontend `Sources` component.

The frontend needs source metadata such as:

- `evidence_id`
- `source_id`
- `guest`
- `title`
- `url`

Without full metadata, `ChatMessage.jsx` could not reliably render useful source links under Ship30 artifact responses.

## Fix

`Ship30Essay` in `backend/app/skills/ship30_skill.py` now preserves the full list of selected `Evidence` objects.

`ArtifactAgent` maps `essay.evidence` into source dictionaries:

- `evidence_id`
- `source_id`
- `guest`
- `title`
- `url`

`ChatService` persists those dictionaries on the assistant message through the `messages.sources` JSONB column.

`ChatMessage.jsx` renders source links from the persisted message source list.

## Validation Result

The Ship30 essay flow was validated locally after the fix. Five sources were returned with transcript metadata, allowing the frontend to display source links for the generated artifact response.

## Current Status

Implemented. Source metadata survives the Ship30 artifact pipeline from grounded `Evidence` through `ArtifactAgent`, `ChatService`, persisted messages, and frontend rendering.
