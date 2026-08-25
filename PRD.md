# Lenny Growth Assistant - Product Requirements Document

## 1. Product Overview

Lenny Growth Assistant is a local web application for asking product-growth questions against Lenny's Podcast transcript evidence and generating grounded Ship30-style written artifacts. The core experience is a persisted chat workspace: users select or create a conversation, ask a question, choose either the chat agent or Ship30 essay agent, receive an answer, and inspect source links attached to assistant responses.

The backend is a FastAPI application backed by PostgreSQL and pgvector. Transcript chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2`, retrieved semantically, filtered by a grounding layer, and passed into agent-specific generation flows. The frontend is a React/Vite/Tailwind interface with a conversation sidebar, message feed, source rendering, and artifact viewer.

## 2. Problem

Users need a way to turn a large collection of Lenny's Podcast transcript material into useful product-growth answers and long-form Ship30-style writing without losing traceability to the underlying source material. A generic chatbot can answer broadly, but it may invent claims, blur sources together, or fail to show where advice came from. This project focuses on evidence-grounded responses from ingested transcripts.

## 3. Target User

The intended user is an evaluator or builder exploring product-growth ideas from the transcript corpus. The current frontend uses a fixed demo user from `frontend/src/data/mockData.js`; authentication and multi-user account management are not implemented.

## 4. User Jobs

- Ask product-growth questions in a persisted chat session.
- Receive concise, grounded answers from transcript evidence.
- Generate Ship30-style essays through the `artifact` agent exposed as "Ship30 Essay" in the UI.
- Generate structured Ship30 plans through the backend `ship30` agent/API path.
- Inspect supporting sources attached to assistant messages.
- Create, view, and delete chat sessions.
- Retrieve persisted artifacts by ID.

## 5. Goals

Primary goals:

- Provide transcript-grounded product-growth answers.
- Preserve source metadata from retrieval through response rendering.
- Generate evidence-grounded Ship30 plans and essays.
- Persist sessions, messages, sources on messages, and artifacts.
- Support local LLM operation through Ollama.

Secondary goals:

- Support Anthropic as an optional cloud LLM provider for provider-based generation.
- Keep retrieval, grounding, generation, agents, and persistence separated.
- Provide a frontend that makes sources and artifacts easy to inspect.

## 6. Non-Goals

- User authentication, signup, login, roles, or permissions.
- Production deployment automation.
- Real-time streaming responses.
- Source ingestion from remote APIs.
- Editing generated artifacts in the UI.
- Copy/export implementation for artifact buttons.
- Admin tools for managing transcripts.
- A guarantee that every script in `backend/scripts/` is part of a stable automated test suite.

## 7. User Flows

### Chat Flow

User -> React chat UI -> `POST /sessions/{session_id}/chat` -> `process_chat()` in `backend/app/services/chat_service.py` -> `AgentDispatcher` -> `ChatAgent` -> `run_grounded_agent()` -> `retrieve_grounded_context()` -> retrieval/grounding -> Claude Agent SDK -> persisted assistant `Message` with `sources` -> frontend `ChatMessage`.

### Ship30 Flow

User/API caller -> `agent="ship30"` -> `Ship30Agent` -> `generate_ship30()` -> `search_similar_chunks()` -> `select_grounded_evidence()` -> `generate_ship30_plan()` -> LLM JSON generation -> `_resolve_evidence_indexes()` -> `Ship30Plan.model_validate()` -> `validate_ship30_plan()` -> rendered plan.

The React input currently exposes `chat` and `artifact`; the backend `ship30` planning agent exists but is not shown as a dropdown option in `ChatInput.jsx`.

### Artifact Flow

User -> `agent="artifact"` from "Ship30 Essay" -> `ArtifactAgent` -> `Ship30SkillService` -> retrieval -> grounding -> `Ship30Skill` -> `Ship30Essay` -> source metadata flattening -> `ChatService` persists assistant message sources -> `create_artifact()` sanitizes and persists essay -> frontend fetches `GET /artifacts/{artifact_id}` -> `ArtifactViewer`.

## 8. Functional Requirements

- Chat: accept non-empty messages up to 10,000 characters through `ChatRequest`.
- Grounded responses: retrieve transcript chunks, select grounded `Evidence`, and answer using supplied transcript evidence only.
- Evidence/source tracking: return sources with available `guest`, `title`, `url`, `distance`, `chunk_index`, and `evidence_id`. Artifact generation also produces `source_id`, but the current `ChatSource` API response schema does not expose `source_id` on the immediate chat response.
- Ship30 plan generation: produce a `Ship30Plan` with `goal`, `principles`, four phases, and `success`.
- Ship30 essay generation: generate approximately 700-word Ship30-style essays through `Ship30Skill`.
- Artifact persistence: store generated essays in the `artifacts` table with session and assistant message references.
- Source display: render source links under assistant responses in `ChatMessage.jsx`.
- Session persistence: create, list, select, load, title, and delete sessions.
- Local LLM support: use Ollama through `OllamaProvider`.
- Cloud LLM support: use Anthropic through `AnthropicProvider` when configured.

## 9. Grounding Requirements

Retrieval candidates come from `search_similar_chunks()` using pgvector cosine distance. Candidates are not automatically treated as evidence. `select_grounded_evidence()` requires topic relevance and combined lexical/topic/semantic relevance before converting candidates to `Evidence`.

`Evidence` includes `evidence_id`, `source_id`, `guest`, `title`, `content`, `chunk_index`, `url`, and `distance`. `build_evidence_id()` creates stable IDs from `source_id` and `chunk_index`.

For structured Ship30 generation, the LLM receives integer `evidence_indexes` such as `[0]` instead of backend evidence IDs. `_resolve_evidence_indexes()` maps those indexes back to real `evidence_id` values before Pydantic validation. `validate_ship30_plan()` then rejects invalid evidence references, unsupported numerical claims, generic actions, weakly supported actions, and weakly supported success criteria.

## 10. Success Metrics

- Grounded response rate: responses return selected sources when evidence exists.
- Valid structured generation rate: Ship30 JSON parses, resolves evidence indexes, and validates.
- Source preservation: assistant messages and artifact flows keep source metadata.
- Successful artifact generation: artifact requests return and persist an `artifact_id`.
- Response latency: local Ollama requests complete within configured timeouts.
- Test pass rate: script-level checks and frontend build complete successfully.

These are evaluator-facing success measures, not measured production analytics.

## 11. Acceptance Criteria

- A user can create a conversation with `POST /sessions`.
- A user can ask a chat question and receive an assistant message persisted to PostgreSQL.
- Assistant responses include source metadata when grounded evidence is selected.
- The frontend renders assistant Markdown and source links.
- A Ship30 plan request validates evidence references after resolving `evidence_indexes`.
- An artifact request creates a Ship30 essay, persists it, returns `artifact_id`, and displays it in `ArtifactViewer`.
- Artifact HTML is sanitized before persistence.
- Missing sessions return 404 through the chat/session API paths.
- Ollama configuration works with `qwen2.5:1.5b` when the model is available locally.
- Anthropic generation fails clearly if selected without `ANTHROPIC_API_KEY` or `ANTHROPIC_MODEL`.

## 12. Risks

- Small local LLM limitations can reduce answer quality and JSON reliability.
- Hallucination remains possible if prompts or validation fail to catch unsupported claims.
- Insufficient evidence can lead to sparse or no answers.
- Retrieval quality depends on embeddings and transcript chunking.
- Long transcript context increases latency and may exceed local model comfort.
- Structured JSON failures can break Ship30 plan generation.
- Source metadata loss can make outputs untrustworthy if evidence is flattened too early.

## 13. Trade-offs

- Local `qwen2.5:1.5b` is inexpensive and private but lower quality and slower on long outputs than larger/cloud models.
- Evidence indexes are simpler for the LLM than backend evidence IDs, but require backend resolution before validation.
- Strict grounding prevents many unsupported claims but can produce shorter or less comprehensive recommendations.
- Transcript context is truncated in the Ship30 essay prompt (`item.content[:3500]`) to keep local generation practical.
- The frontend uses a fixed demo user, which keeps evaluation simple but avoids real authentication.

## 14. Implementation Status

Implemented:

- FastAPI backend with session, chat, and artifact routes.
- PostgreSQL persistence with SQLAlchemy and Alembic.
- pgvector transcript retrieval.
- Sentence Transformer embeddings.
- Grounding service and evidence schema.
- Agent dispatcher/router with `chat`, `ship30`, and `artifact`.
- Ollama and Anthropic provider abstraction.
- Ship30 plan generation and validation.
- Ship30 essay skill and artifact persistence.
- React chat UI, source display, session sidebar, deletion confirmation, and artifact viewer.
- Server-side artifact HTML sanitization.

Partially implemented:

- Cloud LLM support: Anthropic provider exists but requires environment configuration.
- Ship30 plan UI: backend agent exists, but the current frontend dropdown exposes only `Chat` and `Ship30 Essay`.
- Artifact controls: Copy and Export buttons are present visually but do not implement copy/export behavior.
- Artifact timestamp display: `ArtifactHeader.jsx` expects `createdAt`, while `ArtifactResponse` returns `created_at`.
- Immediate chat response source schema: `ChatSource` does not currently include `source_id`, although artifact sources are persisted with it in `Message.sources`.

Future work:

- Authentication and configurable users.
- Deployment configuration.
- A formal test runner and consolidated automated suite.
- UI for structured Ship30 plans.
- Stronger source display for artifacts themselves, not only assistant messages.
