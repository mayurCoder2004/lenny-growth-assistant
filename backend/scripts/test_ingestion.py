from pathlib import Path

from app.services.ingestion_service import (
    chunk_transcript,
    clean_transcript,
    discover_transcripts,
    parse_transcript_file,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]

    transcripts_root = (
        project_root
        / "data"
        / "source-transcripts"
    )

    files = discover_transcripts(
        transcripts_root
    )

    print(f"Found transcripts: {len(files)}")

    if not files:
        raise RuntimeError(
            "No transcript files found."
        )

    first_file = files[0]

    print(f"\nTesting: {first_file}")

    parsed = parse_transcript_file(
        first_file
    )

    cleaned = clean_transcript(
        parsed.transcript
    )

    chunks = chunk_transcript(
        cleaned
    )

    print("\nMetadata")
    print("--------")
    print(f"Guest: {parsed.guest}")
    print(f"Title: {parsed.title}")
    print(f"Video ID: {parsed.video_id}")
    print(f"Published: {parsed.publish_date}")
    print(f"Keywords: {parsed.keywords}")

    print("\nTranscript")
    print("----------")
    print(f"Characters: {len(cleaned)}")
    print(f"Words: {len(cleaned.split())}")
    print(f"Chunks: {len(chunks)}")

    if chunks:
        print("\nFirst chunk")
        print("-----------")
        print(chunks[0][:1000])


if __name__ == "__main__":
    main()