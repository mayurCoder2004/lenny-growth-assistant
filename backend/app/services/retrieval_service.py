from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import TranscriptChunk
from app.services.embedding_service import generate_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Find transcript chunks that are semantically similar
    to the user's query.

    Uses pgvector cosine distance.
    """

    if not query.strip():
        return []

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
        ORDER BY tc.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
        """
    )

    rows = db.execute(
        sql,
        {
            "embedding": embedding_text,
            "limit": limit,
        },
    ).mappings().all()

    results: list[dict[str, Any]] = []

    for row in rows:
        results.append(
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

    return results