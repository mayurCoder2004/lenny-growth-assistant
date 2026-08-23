# Development Log

This document records meaningful AI-assisted development attempts,
failures, corrections, and engineering decisions made while building
The Lenny Growth Assistant.

## Phase 1: Backend and Persistence Foundation

### 1. Database driver issue

**Problem**

SQLAlchemy attempted to use `psycopg2`, but the project was configured with
Psycopg 3.

**Error**

`ModuleNotFoundError: No module named 'psycopg2'`

**Correction**

The SQLAlchemy connection URL was changed from:

`postgresql://`

to:

`postgresql+psycopg://`

This explicitly selects the Psycopg 3 driver.

**Result**

The FastAPI application successfully connected to Neon PostgreSQL.

---

### 2. SQLAlchemy reserved attribute

**Problem**

The `TranscriptChunk` model initially used `metadata` as a Python attribute.

**Error**

`InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.`

**Correction**

The Python attribute was changed to `chunk_metadata`, while the database
column remains named `metadata`.

**Result**

The SQLAlchemy models imported successfully.

---

### 3. Alembic and pgvector migration

**Problem**

Alembic generated a migration containing a pgvector `VECTOR` type without
the required Python import.

**Error**

`NameError: name 'pgvector' is not defined`

**Correction**

The migration was updated to import the pgvector SQLAlchemy type and use
`Vector(384)` for the embedding column.

**Result**

The initial database migration successfully ran against Neon.

---

### 4. Python module import issue

**Problem**

Running the demo-user script directly with:

`python scripts/create_demo_user.py`

caused Python to fail to locate the `app` package.

**Error**

`ModuleNotFoundError: No module named 'app'`

**Correction**

The script was executed as a module:

`python -m scripts.create_demo_user`

**Result**

The demo user was successfully created.

---

### 5. Session and message persistence

Implemented and tested:

- `POST /sessions`
- `GET /sessions/{session_id}`
- `POST /sessions/{session_id}/messages`
- `GET /sessions/{session_id}/messages`

**Result**

Sessions and messages are successfully persisted in Neon PostgreSQL
and retrieved through the FastAPI API.

---

### 6. Session isolation

Two independent sessions were created.

Session A contained a retention conversation.

Session B contained a pricing question.

Retrieving Session A returned only Session A's messages.

**Result**

Independent session context was verified successfully.

---

### Phase 1 result

The backend persistence foundation is complete.

Verified:

- FastAPI application
- Neon PostgreSQL
- SQLAlchemy
- Alembic migrations
- pgvector
- User persistence
- Session persistence
- Message persistence
- Message retrieval
- Session isolation