from app.services.grounding_service import select_grounded_evidence
from app.services.retrieval_service import search_similar_chunks


class FakeMappings:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeDbResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return FakeMappings(self.rows)


class FakeRetrievalDb:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, statement, params):
        self.params = params
        return FakeDbResult(self.rows)


def test_retrieval_returns_relevant_transcript_chunks(monkeypatch):
    monkeypatch.setattr(
        "app.services.retrieval_service.generate_embedding",
        lambda query: [0.1, 0.2, 0.3],
    )

    db = FakeRetrievalDb(
        [
            {
                "id": "chunk-1",
                "source_id": "source-1",
                "content": "Activation improves when onboarding is clear.",
                "chunk_index": 0,
                "title": "Activation",
                "episode": "Guest Name",
                "url": "https://example.com",
                "published_at": None,
                "distance": 0.22,
            }
        ]
    )

    results = search_similar_chunks(
        db=db,
        query="How do I improve activation?",
        limit=5,
        candidate_limit=20,
    )

    assert len(results) == 1
    assert results[0]["guest"] == "Guest Name"
    assert results[0]["distance"] == 0.22
    assert db.params["candidate_limit"] == 20


def test_grounding_filters_irrelevant_evidence():
    candidates = [
        {
            "source_id": "source-1",
            "content": "Activation improves when onboarding is clear.",
            "chunk_index": 0,
            "title": "Activation",
            "guest": "Guest Name",
            "url": None,
            "distance": 0.20,
        },
        {
            "source_id": "source-2",
            "content": "This section discusses office furniture.",
            "chunk_index": 0,
            "title": "Unrelated",
            "guest": "Other Guest",
            "url": None,
            "distance": 0.21,
        },
    ]

    evidence = select_grounded_evidence(
        question="How do I improve activation onboarding?",
        candidates=candidates,
        max_evidence=5,
    )

    assert [item.source_id for item in evidence] == ["source-1"]


def test_grounding_respects_max_evidence_and_empty_retrieval():
    candidates = [
        {
            "source_id": f"source-{index}",
            "content": "Activation onboarding helps users reach value quickly.",
            "chunk_index": index,
            "title": "Activation",
            "guest": "Guest",
            "url": None,
            "distance": 0.20 + (index * 0.01),
        }
        for index in range(4)
    ]

    evidence = select_grounded_evidence(
        question="activation onboarding value",
        candidates=candidates,
        max_evidence=2,
    )

    assert len(evidence) == 2
    assert select_grounded_evidence("activation", []) == []
