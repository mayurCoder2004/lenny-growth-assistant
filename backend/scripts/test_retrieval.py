from app.database import SessionLocal
from app.services.retrieval_service import search_similar_chunks


def main() -> None:
    query = "How should I think about leaving my job?"

    db = SessionLocal()

    try:
        results = search_similar_chunks(
            db=db,
            query=query,
            limit=5,
        )

        print()
        print("Query")
        print("-----")
        print(query)

        print()
        print(f"Results: {len(results)}")

        for index, result in enumerate(
            results,
            start=1,
        ):
            print()
            print(f"Result {index}")
            print("-" * 60)
            print(f"Title: {result['title']}")
            print(f"Guest: {result['guest']}")
            print(f"Chunk: {result['chunk_index']}")
            print(f"Distance: {result['distance']:.4f}")
            print()
            print(result["content"][:700])

    finally:
        db.close()


if __name__ == "__main__":
    main()