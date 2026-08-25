# Backend Test Suite

## Install Test Dependencies

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`pytest` is included in `backend/requirements.txt`.

## Run Tests

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests
```

## Coverage

The focused pytest suite covers:

- Health/API behavior.
- Invalid chat request validation.
- Session creation and retrieval.
- Message persistence and source preservation.
- Session/message isolation.
- Agent routing and unsupported-agent errors.
- Retrieval result shaping.
- Grounding relevance filtering, empty retrieval, and `max_evidence`.
- Ship30 evidence requirements, evidence-index resolution, invalid index rejection, and deterministic validation.
- Artifact persistence, sanitization, and empty-content rejection.
- LLM provider failure and empty-response handling.

## Mocked External Services

The tests do not call external LLMs, Ollama, Anthropic, Hugging Face, or a production transcript database. LLM provider behavior and embedding generation are mocked where needed.

## Credentials

The suite does not require Anthropic credentials and does not require a running Ollama server.
