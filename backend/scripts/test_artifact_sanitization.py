from uuid import uuid4

from app.services.artifact_service import create_artifact


class FakeDB:
    def __init__(self):
        self.added = None
        self.committed = False

    def add(self, artifact):
        self.added = artifact

    def commit(self):
        self.committed = True

    def refresh(self, artifact):
        pass


db = FakeDB()

malicious_content = """
<h1>Safe title</h1>
<p>This is safe content.</p>
<script>alert("xss")</script>
<img src="x" onerror="alert(1)">
<p onclick="alert(2)">Another paragraph</p>
<a href="javascript:alert(3)">Malicious link</a>
<a href="https://example.com">Safe link</a>
"""

artifact = create_artifact(
    db=db,
    session_id=uuid4(),
    message_id=None,
    artifact_type="essay",
    title="Security Test",
    content=malicious_content,
)

result = artifact.content

assert "<script" not in result
assert "<img" not in result
assert "onerror" not in result
assert "onclick" not in result
assert "javascript:" not in result

assert "<h1>Safe title</h1>" in result
assert "<p>This is safe content.</p>" in result
assert 'href="https://example.com"' in result

assert db.committed is True
assert db.added is artifact

print("ARTIFACT PERSISTENCE SANITIZATION TEST PASSED")
print()
print(result)
