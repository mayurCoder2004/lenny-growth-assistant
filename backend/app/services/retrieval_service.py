from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    limit: int = 5,
    candidate_limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Retrieve transcript chunks using pgvector cosine similarity.

    Strategy:
    1. Retrieve a larger candidate pool.
    2. Rank candidates by cosine distance.
    3. Return the strongest candidates.

    Lower cosine distance = higher similarity.
    """

    if not query or not query.strip():
        return []

    if limit <= 0:
        return []

    if candidate_limit < limit:
        candidate_limit = limit

    query_embedding = generate_embedding(query)

    embedding_text = "[" + ",".join(
        str(float(value))
        for value in query_embedding
    ) + "]"

    sql = text(
        """
        SELECT
            tc.id,
            tc.source_id,
            tc.content,
            tc.chunk_index,
            s.title,
            s.episode,
            s.url,
            s.published_at,
            tc.embedding <=> CAST(:embedding AS vector) AS distance
        FROM transcript_chunks tc
        JOIN sources s
            ON s.id = tc.source_id
        WHERE tc.embedding IS NOT NULL
        ORDER BY tc.embedding <=> CAST(:embedding AS vector)
        LIMIT :candidate_limit
        """
    )

    rows = db.execute(
        sql,
        {
            "embedding": embedding_text,
            "candidate_limit": candidate_limit,
        },
    ).mappings().all()

    candidates: list[dict[str, Any]] = []

    for row in rows:
        candidates.append(
            {
                "id": str(row["id"]),
                "source_id": str(row["source_id"]),
                "content": row["content"],
                "chunk_index": row["chunk_index"],
                "title": row["title"],
                "guest": row["episode"],
                "url": row["url"],
                "published_at": row["published_at"],
                "distance": float(row["distance"]),
            }
        )

    if not candidates:
        return []

    # The SQL query already sorts by cosine distance.
    # Lower distance means stronger semantic similarity.
    return candidates[:limit]