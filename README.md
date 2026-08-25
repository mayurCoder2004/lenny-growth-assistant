# Lenny Growth Assistant

Lenny Growth Assistant is an evidence-grounded product-growth assistant for Lenny's Podcast transcripts. It provides a persisted chat workspace, transcript-backed answers, Ship30-style essay generation, source display, and artifact persistence.

## Features

- Persisted chat sessions and messages.
- Grounded answers from ingested transcript chunks.
- Source links attached to assistant responses.
- Ship30-style essay generation through the artifact agent.
- Structured Ship30 plan generation through the backend `ship30` agent.
- PostgreSQL + pgvector semantic retrieval.
- Ollama local LLM support with `qwen2.5:1.5b`.
- Optional Anthropic provider support.
- Server-side artifact HTML sanitization.
- React frontend with conversation sidebar and artifact viewer.

## Architecture

The app is a React/Vite frontend calling a FastAPI backend. The backend stores sessions, messages, sources, transcript chunks, and artifacts in PostgreSQL. Retrieval uses Sentence Transformer embeddings and pgvector; grounding filters candidate chunks before LLM generation.

See [architecture.md](architecture.md) for the detailed system design.

## Quick Start

Prerequisites:

1. Docker Desktop
2. Ollama
3. Git

Ollama remains host-side for the local demo. Install Ollama separately, then pull and verify the required local model:

```powershell
ollama pull qwen2.5:1.5b
ollama run qwen2.5:1.5b "Reply with exactly: OK"
```

Start the application:

```powershell
git clone <repo>
cd lenny-growth-assistant
copy .env.example .env
docker compose up --build
```

Or on Windows PowerShell from the repository root:

```powershell
.\scripts\start.ps1
```

Docker Compose starts:

- PostgreSQL with pgvector on `localhost:5432`
- FastAPI backend on `http://127.0.0.1:8000`
- React/Vite frontend on `http://127.0.0.1:5173`

Health checks:

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/database
```

Inspect logs:

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

Stop the system:

```powershell
docker compose down
```

Reset the local Docker database:

```powershell
docker compose down -v
docker compose up --build
```

The startup is one Docker Compose command after the required host-side Ollama model is installed.

## Tech Stack

- Frontend: React 19, Vite, Tailwind CSS 4, `react-markdown`.
- Backend: FastAPI, SQLAlchemy 2, Pydantic 2, Alembic.
- Database: PostgreSQL with pgvector.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` with 384-dimensional vectors.
- LLMs: Ollama local provider and Anthropic provider.
- Sanitization: `nh3`.

## Project Structure

```text
backend/
  app/
    agents/       Agent router, dispatcher, chat, Ship30, artifact agents
    api/          FastAPI routers
    llm/          LLM provider abstraction
    schemas/      Pydantic schemas
    services/     Retrieval, grounding, chat, artifact, ingestion services
    skills/       Ship30 writing skill
    models.py     SQLAlchemy models
  migrations/     Alembic migrations
  scripts/        Ingestion, debug, and script-level tests
data/
  source-transcripts/
frontend/
  src/
    api/
    components/
    data/
agent-transcripts/
```

## Local Prerequisites Without Docker

- Python 3.11+ recommended for the backend dependency set.
- Node.js and npm for the Vite frontend.
- PostgreSQL with the pgvector extension available.
- Ollama for local LLM use.
- `qwen2.5:1.5b` pulled locally for the default configuration.
- Optional Anthropic API access if using `LLM_PROVIDER=anthropic`.

## Environment Setup

Create a root `.env` from `.env.example` and fill in local values. The defaults are set for Docker Compose. For running the backend directly on the host, use a host-reachable database URL and `OLLAMA_BASE_URL=http://localhost:11434`.

```env
POSTGRES_DB=lenny_growth_assistant
POSTGRES_USER=lenny
POSTGRES_PASSWORD=lenny
POSTGRES_PORT=5432
DATABASE_URL=postgresql://lenny:lenny@postgres:5432/lenny_growth_assistant
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
DOCKER_OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:1.5b
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=
BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_API_BASE_URL=http://127.0.0.1:8000
DEMO_USER_ID=32f8bbc3-60fb-4995-8473-9ff1d14ce88e
APP_ENV=development
LOG_LEVEL=INFO
```

Do not commit real secrets.

## Ollama Setup

```powershell
ollama pull qwen2.5:1.5b
ollama list
ollama run qwen2.5:1.5b
```

The default backend provider expects Ollama at `http://localhost:11434`.

Inside Docker Compose, the backend uses `DOCKER_OLLAMA_BASE_URL`, defaulting to `http://host.docker.internal:11434`, so the container can reach the host Ollama service.

## Backend Setup

From `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.create_demo_user
```

The frontend demo user ID in `frontend/src/data/mockData.js` must exist in the database for the current UI to load sessions successfully.

## Frontend Setup

From `frontend/`:

```powershell
npm install
npm run dev
```

Available frontend scripts from `frontend/package.json`:

- `npm run dev`
- `npm run build`
- `npm run lint`
- `npm run preview`

## Database Setup

Migrations are managed by Alembic under `backend/migrations/`.

From `backend/`:

```powershell
alembic upgrade head
```

The initial migration creates `users`, `sessions`, `messages`, `sources`, `transcript_chunks`, and `artifacts`. A later migration adds `messages.sources` JSONB.

## Transcript / Data Ingestion

Transcript ingestion reads Markdown files from:

```text
data/source-transcripts/episodes/**/transcript.md
```

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m scripts.ingest_one
.\.venv\Scripts\python.exe -m scripts.ingest_all
.\.venv\Scripts\python.exe -m scripts.ingest_all --force
```

`ingest_all.py` skips existing transcripts unless `--force` is supplied.

## Running the Application

Backend, from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend, from `frontend/`:

```powershell
npm run dev
```

The frontend API clients currently call `http://127.0.0.1:8000`.
This can be overridden for Vite with `VITE_API_BASE_URL`.

## Testing

The repository uses script-level backend checks in `backend/scripts/` and Vite build/lint commands for the frontend. There is no separate `tests/` directory or configured pytest runner.

Useful backend checks from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m scripts.test_grounding_logic
.\.venv\Scripts\python.exe -m scripts.test_ship30_generation
.\.venv\Scripts\python.exe -m scripts.test_plan_validation
.\.venv\Scripts\python.exe -m scripts.test_artifact_agent
.\.venv\Scripts\python.exe -m scripts.test_chat_artifact_persistence
.\.venv\Scripts\python.exe -m scripts.test_artifact_sanitization
```

Some older scripts in `backend/scripts/` may reflect earlier contracts. For example, scripts that construct `Ship30Essay(evidence_ids=...)` are stale because the current dataclass stores full `evidence` objects.

Frontend checks from `frontend/`:

```powershell
npm run build
npm run lint
```

Development history records local verification of the Ship30 essay flow and source display in `agent-transcripts/development-log.md`.

## Ship30 Demo

1. Start PostgreSQL, Ollama, backend, and frontend.
2. Open the Vite app.
3. Create or select a conversation.
4. Choose `Ship30 Essay`.
5. Ask: `How can I improve product growth?`

Expected behavior: the assistant generates a Ship30-style essay, sources appear under the assistant message when evidence is found, and the persisted artifact appears in the artifact viewer with status `Saved`.

## Sources

Sources come from grounded `Evidence` objects selected from transcript chunks. Assistant message sources may include `evidence_id`, `source_id`, `guest`, `title`, `url`, `distance`, and `chunk_index`. The frontend renders source links in `ChatMessage.jsx`.

## Artifact Generation

Artifact generation uses `ArtifactAgent`, `Ship30SkillService`, and `Ship30Skill`. The generated essay is sanitized by `create_artifact()` before being stored in PostgreSQL. The chat response returns `artifact_id`, and the frontend retrieves the artifact with `GET /artifacts/{artifact_id}`.

## Troubleshooting

- Ollama not running: start Ollama and verify `OLLAMA_BASE_URL`.
- Model missing: run `ollama pull qwen2.5:1.5b`.
- PostgreSQL connection failure: check `DATABASE_URL` and run `GET /health/database`.
- Missing demo user: run `python -m scripts.create_demo_user` or align `mockData.js` with an existing user.
- Insufficient evidence: ingest transcripts and verify retrieval with `scripts.debug_retrieval`.
- LLM JSON failures: retry or use a stronger configured provider for Ship30 structured plans.
- Local LLM latency: `qwen2.5:1.5b` can be slow on CPU, especially for long essays.

## Configuration

Configuration is defined in `.env.example` and read by `backend/app/config.py`.

- `DATABASE_URL`: PostgreSQL connection string.
- `LLM_PROVIDER`: `ollama` or `anthropic`.
- `OLLAMA_BASE_URL`: local Ollama base URL.
- `DOCKER_OLLAMA_BASE_URL`: Ollama URL used by the backend container.
- `OLLAMA_MODEL`: local model name, default `qwen2.5:1.5b`.
- `ANTHROPIC_API_KEY`: optional cloud provider key.
- `ANTHROPIC_MODEL`: required when `LLM_PROVIDER=anthropic`.
- `VITE_API_BASE_URL`: browser-facing backend URL for the frontend.
- `DEMO_USER_ID`: seeded demo user ID used by the current frontend.
- `APP_ENV`, `LOG_LEVEL`: documented environment fields; not broadly used by application code.

## Security Notes

Keep real secrets out of Git. Artifact content is sanitized server-side with `nh3` before persistence. Authentication and authorization are not implemented.

## Known Limitations

- The frontend uses a fixed demo user.
- The backend `ship30` planning agent is not exposed in the frontend selector.
- Copy/export artifact buttons are visual only.
- `ArtifactHeader.jsx` reads `artifact.createdAt`, while the API returns `created_at`; the timestamp display may be blank until this is mapped in the frontend.
- Local `qwen2.5:1.5b` quality and latency are limited.
- Long transcript context is truncated for essay generation.
- No deployment pipeline is included.

## Development History

See `agent-transcripts/` for development notes, debugging transcripts, and evaluator handoff context.
