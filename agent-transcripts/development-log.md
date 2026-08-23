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



---

## Phase 2: Transcript Ingestion and Semantic Retrieval

### 1. Transcript dataset integration

**Problem**

The application needed a knowledge base containing Lenny's Podcast transcripts
that could be searched when answering user questions.

**Implementation**

The Lenny transcript dataset was added under:

`data/source-transcripts/`

The dataset contained 303 transcript entries.

The transcript files were kept out of Git using `.gitignore` because the raw
transcript dataset is local application data rather than source code.

**Result**

The ingestion pipeline successfully discovered all 303 transcript files.

---

### 2. Transcript parsing and chunking

**Implementation**

Created:

`backend/app/services/ingestion_service.py`

The ingestion service:

- Reads transcript Markdown files
- Extracts transcript metadata
- Extracts guest information
- Extracts title information
- Extracts publication dates
- Splits transcripts into searchable chunks
- Generates embeddings for the chunks
- Stores the source and chunks in PostgreSQL

A test transcript contained:

- 86,086 characters
- 15,807 words
- 16 chunks

**Result**

Transcript parsing and chunking were successfully verified.

---

### 3. Embedding generation

**Problem**

Semantic retrieval requires numerical vector representations of transcript
chunks.

**Implementation**

Added:

`backend/app/services/embedding_service.py`

The project uses:

`sentence-transformers/all-MiniLM-L6-v2`

The model generates embeddings with:

`384 dimensions`

**Verification**

The embedding service was tested with:

`How can I improve product retention?`

The generated embedding successfully returned a vector with 384 dimensions.

**Result**

Embedding generation is working successfully.

---

### 4. Hugging Face model download

**Problem**

The first embedding test required downloading the
`all-MiniLM-L6-v2` model from Hugging Face.

**Observation**

Hugging Face displayed a warning about unauthenticated requests:

`You are sending unauthenticated requests to the HF Hub.`

This did not prevent the model from downloading or being used.

**Result**

The model was downloaded successfully and cached locally.

The embedding test completed successfully.

---

### 5. Semantic retrieval

**Implementation**

Created:

`backend/app/services/retrieval_service.py`

The retrieval service:

1. Converts a user query into an embedding.
2. Compares the query embedding against stored transcript embeddings.
3. Uses vector similarity to find relevant transcript chunks.
4. Returns the most relevant chunks.

**Test query**

`How should I think about leaving my job?`

**Result**

The retrieval system returned 5 relevant chunks from Ada Chen Rekhi's
episode.

The highest-ranked result was directly related to the question and discussed
feeling trapped in a job, career alignment, meaningfulness, and deciding
whether to leave.

Semantic retrieval was successfully verified.

---

### 6. Single transcript ingestion

Created:

`backend/scripts/ingest_one.py`

The script was used to verify the complete ingestion pipeline with a single
transcript.

**Result**

The Ada Chen Rekhi transcript was successfully ingested:

- Source ID generated successfully
- Guest metadata stored
- Transcript chunks stored
- 16 chunks generated
- Embeddings generated successfully

Database verification:

- Sources: 1
- Chunks: 16

---

### 7. Bulk transcript ingestion

Created:

`backend/scripts/ingest_all.py`

The bulk ingestion script processes all available transcript files while
skipping transcripts that have already been ingested.

**Result**

303 transcripts were processed.

Final ingestion summary:

- Total transcripts: 303
- Successful: 271
- Skipped: 32
- Failed: 0
- New chunks: 4,230

The skipped transcripts were already present or otherwise handled by the
duplicate/ingestion logic.

---

### 8. Database verification after bulk ingestion

After bulk ingestion, PostgreSQL was queried directly to verify persistence.

**Result**

- Sources: 272
- Transcript chunks: 4,246
- Failed ingestions: 0

The additional records include the previously ingested Ada Chen Rekhi
transcript and the successfully processed bulk dataset.

---

### 9. Duplicate ingestion handling

During bulk ingestion, several transcript entries were reported as:

`SKIPPED`

This confirmed that the ingestion pipeline does not blindly create duplicate
records when a transcript has already been processed.

Examples included duplicate or alternate transcript entries such as:

- Andy Raskin
- Elena Verna
- Julie Zhuo
- Dylan Field
- Uri Levine
- Wes Kao

**Result**

The ingestion pipeline can safely be rerun without unnecessarily duplicating
already-ingested sources.

---

### Phase 2 result

The knowledge ingestion and semantic retrieval foundation is complete.

Verified:

- 303 transcript files discovered
- Transcript metadata extraction
- Transcript parsing
- Transcript chunking
- Sentence Transformer embeddings
- 384-dimensional embeddings
- PostgreSQL vector storage
- Bulk ingestion
- Duplicate handling
- Semantic similarity search
- Retrieval of relevant transcript chunks
- 272 sources stored
- 4,246 transcript chunks stored
- 0 failed bulk ingestions

**Git commit**

`b0ac177`

`feat: add transcript ingestion and semantic retrieval`

The Phase 2 implementation was pushed successfully to the GitHub repository.