from app.database import SessionLocal
from app.services.rag_service import answer_question


def main():
    question = "How should I think about leaving my job?"

    db = SessionLocal()

    try:
        result = answer_question(
            db=db,
            question=question,
            top_k=5,
            distance_threshold=0.70,
        )

        print("\n" + "=" * 80)
        print("FINAL RESULT")
        print("=" * 80)

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")

        for index, source in enumerate(
            result["sources"],
            start=1,
        ):
            print(
                f"{index}. "
                f"{source.get('guest')} | "
                f"distance={source.get('distance')} | "
                f"chunk={source.get('chunk_index')}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()