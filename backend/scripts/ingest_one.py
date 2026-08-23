from pathlib import Path

from app.database import SessionLocal
from app.services.ingestion_service import ingest_transcript


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]

    transcript_path = (
        project_root
        / "data"
        / "source-transcripts"
        / "episodes"
        / "ada-chen-rekhi"
        / "transcript.md"
    )

    if not transcript_path.exists():
        raise FileNotFoundError(
            f"Transcript not found: {transcript_path}"
        )

    db = SessionLocal()

    try:
        result = ingest_transcript(
            db=db,
            file_path=transcript_path,
        )

        print("\nIngestion successful")
        print("--------------------")
        print(f"Source ID: {result['source_id']}")
        print(f"Title: {result['title']}")
        print(f"Guest: {result['guest']}")
        print(f"Chunks: {result['chunks']}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()