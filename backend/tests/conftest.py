from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest


os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+pysqlite:///:memory:",
)
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:1.5b")

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class ScalarResult:
    def __init__(self, values):
        self.values = values

    def all(self):
        return list(self.values)


class FakePersistenceDb:
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.messages = {}
        self.artifacts = {}
        self.commits = 0
        self.deleted = []

    def add(self, instance):
        from app.models import Artifact, Message, Session, User

        if getattr(instance, "id", None) is None:
            instance.id = uuid.uuid4()

        if isinstance(instance, User):
            self.users[instance.id] = instance
        elif isinstance(instance, Session):
            self.sessions[instance.id] = instance
        elif isinstance(instance, Message):
            self.messages[instance.id] = instance
        elif isinstance(instance, Artifact):
            self.artifacts[instance.id] = instance
        else:
            raise AssertionError(f"Unexpected model: {type(instance)!r}")

    def commit(self):
        self.commits += 1

    def refresh(self, instance):
        return None

    def delete(self, instance):
        from app.models import Session

        self.deleted.append(instance)

        if isinstance(instance, Session):
            self.sessions.pop(instance.id, None)
            self.messages = {
                message_id: message
                for message_id, message in self.messages.items()
                if message.session_id != instance.id
            }

    def get(self, model, model_id):
        from app.models import Artifact, Message, Session, User

        stores = {
            User: self.users,
            Session: self.sessions,
            Message: self.messages,
            Artifact: self.artifacts,
        }

        return stores[model].get(model_id)

    def scalars(self, statement):
        from app.models import Message, Session

        text = str(statement)

        if "FROM messages" in text:
            session_id = statement.compile().params.get("session_id_1")
            values = [
                message
                for message in self.messages.values()
                if message.session_id == session_id
            ]
            return ScalarResult(values)

        if "FROM sessions" in text:
            user_id = statement.compile().params.get("user_id_1")
            values = [
                session
                for session in self.sessions.values()
                if session.user_id == user_id
            ]
            return ScalarResult(values)

        raise AssertionError(f"Unexpected scalar statement: {text}")


@pytest.fixture
def fake_db():
    return FakePersistenceDb()


@pytest.fixture
def sample_evidence():
    from app.schemas.evidence import Evidence

    return [
        Evidence(
            evidence_id="source-1-0",
            source_id="source-1",
            guest="Ada Chen Rekhi",
            title="Finding Product-Market Fit",
            content=(
                "Activation improves when onboarding helps users "
                "experience product value quickly."
            ),
            chunk_index=0,
            url="https://example.com/ada",
            distance=0.25,
        )
    ]
