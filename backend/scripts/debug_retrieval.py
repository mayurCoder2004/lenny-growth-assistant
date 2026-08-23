from app.database import SessionLocal
from app.services.retrieval_service import search_similar_chunks


QUERIES = [
    "How should I think about leaving my job?",
    "When should I leave my job?",
    "How do I know if I am stuck in my career?",
    "Should I quit my job?",
    "How do I decide whether to stay or leave a company?",
]


def main():
    db = SessionLocal()

    try:
        for query in QUERIES:
            print("\n" + "=" * 100)
            print(f"QUERY: {query}")
            print("=" * 100)

            results = search_similar_chunks(
                db=db,
                query=query,
                limit=5,
                candidate_limit=20,
            )

            for index, result in enumerate(results, start=1):
                print(
                    f"\n{index}. "
                    f"{result['guest']} | "
                    f"distance={result['distance']:.4f} | "
                    f"chunk={result['chunk_index']}"
                )

                print(f"   Episode: {result['title']}")
                print(f"   Content: {result['content'][:500]}...")


    finally:
        db.close()


if __name__ == "__main__":
    main()