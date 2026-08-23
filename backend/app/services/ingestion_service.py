from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.orm import Session

from app.models import Source, TranscriptChunk
from app.services.embedding_service import generate_embeddings


@dataclass
class ParsedTranscript:
    guest: str
    title: str
    youtube_url: str | None
    video_id: str | None
    publish_date: str | date | datetime | None
    description: str | None
    duration_seconds: float | None
    duration: str | None
    view_count: int | None
    channel: str | None
    keywords: list[str]
    transcript: str
    source_path: str


def parse_transcript_file(
    file_path: Path,
) -> ParsedTranscript:
    """
    Parse one Lenny's Podcast transcript Markdown file.

    Expected structure:

    ---
    YAML frontmatter
    ---

    Markdown transcript
    """

    content = file_path.read_text(
        encoding="utf-8",
    )

    if not content.startswith("---"):
        raise ValueError(
            f"Missing YAML frontmatter: {file_path}"
        )

    parts = content.split("---", 2)

    if len(parts) != 3:
        raise ValueError(
            f"Invalid transcript format: {file_path}"
        )

    frontmatter_text = parts[1]
    transcript_text = parts[2].strip()

    metadata: dict[str, Any] = (
        yaml.safe_load(frontmatter_text) or {}
    )

    return ParsedTranscript(
        guest=str(metadata.get("guest", "")),
        title=str(metadata.get("title", "")),
        youtube_url=metadata.get("youtube_url"),
        video_id=metadata.get("video_id"),
        publish_date=metadata.get("publish_date"),
        description=metadata.get("description"),
        duration_seconds=metadata.get("duration_seconds"),
        duration=metadata.get("duration"),
        view_count=metadata.get("view_count"),
        channel=metadata.get("channel"),
        keywords=metadata.get("keywords") or [],
        transcript=transcript_text,
        source_path=str(file_path),
    )


def discover_transcripts(
    transcripts_root: Path,
) -> list[Path]:
    """
    Discover every transcript.md file in the archive.
    """

    return sorted(
        transcripts_root.glob(
            "episodes/**/transcript.md"
        )
    )


def clean_transcript(
    transcript: str,
) -> str:
    """
    Perform conservative transcript cleaning.

    We intentionally avoid aggressive transformations
    so that the source meaning is preserved.
    """

    lines = [
        line.strip()
        for line in transcript.splitlines()
    ]

    cleaned_lines = [
        line
        for line in lines
        if line
    ]

    return "\n".join(cleaned_lines)


def chunk_transcript(
    transcript: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    """
    Split transcript into overlapping word-based chunks.

    chunk_size:
        Approximate number of words per chunk.

    overlap:
        Number of words repeated between adjacent chunks.
    """

    words = transcript.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks: list[str] = []

    start = 0

    while start < len(words):
        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def _parse_publish_date(
    value: str | date | datetime | None,
) -> datetime | None:
    """
    Convert transcript publish date to datetime.

    PyYAML automatically converts values such as:

        2023-04-21

    into datetime.date objects, so we support both
    strings and date objects.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(
            value,
            datetime.min.time(),
        )

    return datetime.strptime(
        value,
        "%Y-%m-%d",
    )


def _find_existing_source(
    db: Session,
    parsed: ParsedTranscript,
) -> Source | None:
    """
    Find an existing source.

    YouTube URL is the preferred stable identifier.
    """

    if parsed.youtube_url:
        source = (
            db.query(Source)
            .filter(
                Source.url == parsed.youtube_url
            )
            .first()
        )

        if source:
            return source

    return (
        db.query(Source)
        .filter(
            Source.title == parsed.title
        )
        .first()
    )


def ingest_transcript(
    db: Session,
    file_path: Path,
    embedding_batch_size: int = 16,
) -> dict[str, Any]:
    """
    Ingest one transcript into PostgreSQL.

    Steps:

    1. Parse metadata and transcript.
    2. Clean transcript.
    3. Create chunks.
    4. Find or create Source.
    5. Remove old chunks for deterministic re-ingestion.
    6. Generate embeddings.
    7. Store TranscriptChunk records.
    8. Commit transaction.
    """

    parsed = parse_transcript_file(
        file_path
    )

    transcript = clean_transcript(
        parsed.transcript
    )

    chunks = chunk_transcript(
        transcript
    )

    if not chunks:
        raise ValueError(
            f"No transcript content found: {file_path}"
        )

    source = _find_existing_source(
        db,
        parsed,
    )

    if source is None:
        source = Source(
            title=parsed.title,
            episode=parsed.guest,
            url=parsed.youtube_url,
            published_at=_parse_publish_date(
                parsed.publish_date
            ),
        )

        db.add(source)
        db.flush()

    else:
        # Keep source metadata up to date if the
        # source is re-ingested.
        source.title = parsed.title
        source.episode = parsed.guest
        source.url = parsed.youtube_url
        source.published_at = _parse_publish_date(
            parsed.publish_date
        )

    # Remove existing chunks before recreating them.
    # This makes repeated ingestion deterministic.
    db.query(TranscriptChunk).filter(
        TranscriptChunk.source_id == source.id
    ).delete(
        synchronize_session=False
    )

    embeddings = generate_embeddings(
        chunks,
        batch_size=embedding_batch_size,
    )

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Embedding count does not match chunk count."
        )

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        transcript_chunk = TranscriptChunk(
            source_id=source.id,
            content=chunk,
            chunk_index=index,
            embedding=embedding,
        )

        db.add(transcript_chunk)

    db.commit()

    return {
        "source_id": str(source.id),
        "title": parsed.title,
        "guest": parsed.guest,
        "chunks": len(chunks),
        "source_path": str(file_path),
    }