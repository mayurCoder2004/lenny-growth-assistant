# Deployment and Reproducible Startup

## Local Topology

The evaluator workflow uses Docker Compose for application infrastructure and host-side Ollama for local LLM generation.

Docker Compose starts:

- `postgres`: PostgreSQL 16 with pgvector.
- `backend`: FastAPI app from `backend/Dockerfile`.
- `frontend`: React/Vite app from `frontend/Dockerfile`.

Host-side dependency:

- Ollama running on the evaluator machine with `qwen2.5:1.5b` installed.

## Why Ollama Is Host-Side

The assignment demo uses a local Ollama model. Keeping Ollama on the host avoids building a large model-serving container, avoids GPU/CPU passthrough differences across evaluator machines, and matches the normal local Ollama workflow.

The backend container reaches host Ollama with:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

`docker-compose.yml` also sets:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This supports Docker Desktop on Windows/macOS and common Linux Docker setups.

## Quick Start

From the repository root:

```powershell
copy .env.example .env
ollama pull qwen2.5:1.5b
ollama run qwen2.5:1.5b "Reply with exactly: OK"
docker compose up --build
```

PowerShell helper:

```powershell
.\scripts\start.ps1
```

The helper creates `.env` from `.env.example` if needed, then runs `docker compose up --build`.

## Service URLs

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- Backend health: `http://127.0.0.1:8000/health`
- Database health: `http://127.0.0.1:8000/health/database`
- PostgreSQL: `localhost:5432`

## Docker Services

### PostgreSQL / pgvector

`postgres` uses the `pgvector/pgvector:pg16` image. The init script at `docker/postgres/init.sql` runs:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Data is stored in the named Docker volume `postgres_data`.

### FastAPI Backend

The backend image installs `backend/requirements.txt`, copies the app, waits for PostgreSQL to accept TCP connections, runs Alembic migrations, seeds the demo user, and starts:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The demo user seed uses `DEMO_USER_ID`, defaulting to the same UUID used by `frontend/src/data/mockData.js`.

### React/Vite Frontend

The frontend image installs dependencies with `npm ci` and starts Vite with:

```powershell
npm run dev -- --host 0.0.0.0
```

The browser-facing API URL is configured with `VITE_API_BASE_URL`.

## Environment Variables

The Compose defaults in `.env.example` are:

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

No Anthropic key is required for the default local workflow.

## Startup Sequence

1. PostgreSQL starts and initializes pgvector.
2. Docker healthcheck waits for PostgreSQL readiness.
3. Backend waits for PostgreSQL TCP availability.
4. Backend runs `alembic upgrade head`.
5. Backend runs `python -m scripts.create_demo_user`.
6. Backend starts FastAPI.
7. Frontend starts Vite and calls the backend through `VITE_API_BASE_URL`.

## Migrations

Migrations are run automatically during backend container startup. To run them manually:

```powershell
docker compose run --rm backend alembic upgrade head
```

## Transcript Ingestion

The Compose workflow starts the app and database, but it does not automatically ingest the local transcript dataset. After the stack is running, ingest data with:

```powershell
docker compose run --rm backend python -m scripts.ingest_all
```

Force re-ingestion:

```powershell
docker compose run --rm backend python -m scripts.ingest_all --force
```

The repository ignores `data/source-transcripts/`, so evaluators need the transcript dataset locally for ingestion.

## Logs

```powershell
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

## Stop and Reset

Stop containers:

```powershell
docker compose down
```

Stop and delete the local database volume:

```powershell
docker compose down -v
```

Then restart:

```powershell
docker compose up --build
```

## Troubleshooting

- PostgreSQL unavailable: check `docker compose logs postgres` and `docker compose ps`.
- pgvector errors: reset the volume with `docker compose down -v` so `docker/postgres/init.sql` runs on a fresh database.
- Backend migration failure: inspect `docker compose logs backend`.
- Ollama unavailable: verify `ollama run qwen2.5:1.5b "Reply with exactly: OK"` on the host.
- Backend cannot reach Ollama: verify `OLLAMA_BASE_URL=http://host.docker.internal:11434` in `.env`.
- Empty or weak answers: verify transcript data has been ingested.
- Frontend API errors: verify `VITE_API_BASE_URL=http://127.0.0.1:8000` and check `GET /health`.

## Windows Notes

- Use Docker Desktop with Linux containers.
- Use PowerShell `copy .env.example .env` or run `.\scripts\start.ps1`.
- If Docker reports user config permission warnings, Docker may still work; verify with `docker compose version`.
- If port `5432`, `8000`, or `5173` is already in use, change `POSTGRES_PORT`, `BACKEND_PORT`, or `FRONTEND_PORT` in `.env`.

## Limitations

- This is a local reproducible workflow, not a production deployment.
- Ollama remains a host dependency.
- Transcript ingestion is a separate step because the transcript dataset is local ignored data.
- The frontend uses the seeded demo user rather than authentication.
