from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    all-MiniLM-L6-v2 produces 384-dimensional embeddings,
    which matches the pgvector column in our database.
    """

    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate a normalized embedding for one text chunk.
    """

    if not text.strip():
        raise ValueError(
            "Cannot generate an embedding for empty text."
        )

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def generate_embeddings(
    texts: list[str],
    batch_size: int = 16,
) -> list[list[float]]:
    """
    Generate embeddings for multiple text chunks.

    Small batches are intentional because the development
    machine has limited RAM.
    """

    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError(
            "Cannot generate embeddings for empty text."
        )

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return embeddings.tolist()