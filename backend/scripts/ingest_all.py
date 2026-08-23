from pathlib import Path
import sys

from app.database import SessionLocal
from app.services.ingestion_service import (
    ingest_transcript,
    parse_transcript_file,
)
from app.models import Source


def main() -> None:
    force = "--force" in sys.argv

    project_root = Path(__file__).resolve().parents[2]

    transcripts_root = (
        project_root
        / "data"
        / "source-transcripts"
    )

    transcript_files = sorted(
        transcripts_root.glob(
            "episodes/**/transcript.md"
        )
    )

    total = len(transcript_files)

    if total == 0:
        print("No transcript files found.")
        return

    print(f"Found {total} transcripts.")

    if force:
        print("FORCE MODE: existing transcripts will be re-ingested.")

    print()

    db = SessionLocal()

    successful = 0
    skipped = 0
    failed = 0
    total_chunks = 0

    try:
        for index, file_path in enumerate(
            transcript_files,
            start=1,
        ):
            try:
                parsed = parse_transcript_file(
                    file_path
                )

                existing = None

                if parsed.youtube_url:
                    existing = (
                        db.query(Source)
                        .filter(
                            Source.url == parsed.youtube_url
                        )
                        .first()
                    )

                if existing is None:
                    existing = (
                        db.query(Source)
                        .filter(
                            Source.title == parsed.title
                        )
                        .first()
                    )

                if existing is not None and not force:
                    skipped += 1

                    print(
                        f"[{index}/{total}] "
                        f"{parsed.guest} "
                        f"-> SKIPPED"
                    )

                    continue

                result = ingest_transcript(
                    db=db,
                    file_path=file_path,
                )

                successful += 1
                total_chunks += result["chunks"]

                print(
                    f"[{index}/{total}] "
                    f"{parsed.guest} "
                    f"-> OK "
                    f"({result['chunks']} chunks)"
                )

            except Exception as exc:
                failed += 1

                db.rollback()

                print(
                    f"[{index}/{total}] "
                    f"{file_path.parent.name} "
                    f"-> FAILED"
                )

                print(
                    f"    Error: {exc}"
                )

        print()
        print("=" * 60)
        print("INGESTION SUMMARY")
        print("=" * 60)
        print(f"Total transcripts : {total}")
        print(f"Successful        : {successful}")
        print(f"Skipped           : {skipped}")
        print(f"Failed            : {failed}")
        print(f"New chunks        : {total_chunks}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()