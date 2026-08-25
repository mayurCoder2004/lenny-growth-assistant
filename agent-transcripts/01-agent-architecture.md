# Agent Architecture Transcript

## Summary

The project separates request orchestration, routing, and specialized agent behavior instead of putting all generation logic inside the chat endpoint.

## Implemented Files

- `backend/app/agents/base.py`
- `backend/app/agents/router.py`
- `backend/app/agents/dispatcher.py`
- `backend/app/agents/chat_agent.py`
- `backend/app/agents/ship30_agent.py`
- `backend/app/agents/artifact_agent.py`
- `backend/app/services/chat_service.py`

## Decision

`ChatService` owns the conversation lifecycle: validate the session, persist the user message, dispatch the request, persist the assistant message, and persist an artifact when the selected agent is `artifact`.

`AgentDispatcher` owns generic dispatch. `AgentRouter` maps names to concrete agents:

- `chat` -> `ChatAgent`
- `ship30` -> `Ship30Agent`
- `artifact` -> `ArtifactAgent`

## Why Responsibilities Are Separated

- The chat API remains stable while agent implementations can differ.
- Chat, Ship30 plan generation, and artifact generation have different outputs and validation needs.
- Retrieval and grounding stay in services so multiple agents can reuse them.
- Artifact persistence stays in `ChatService`/`ArtifactService`, not in the writing skill.

## Current Status

Implemented. The frontend exposes `chat` and `artifact` through `ChatInput.jsx`. The backend also supports the `ship30` agent, but it is not currently exposed in the frontend dropdown.
