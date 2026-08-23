from app.services.embedding_service import generate_embedding


def main() -> None:
    text = (
        "Product retention improves when users repeatedly "
        "experience meaningful value from a product."
    )

    embedding = generate_embedding(text)

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First five values: {embedding[:5]}")


if __name__ == "__main__":
    main()