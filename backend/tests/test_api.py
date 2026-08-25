from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_successfully():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "lenny-growth-assistant",
    }


def test_invalid_chat_request_is_rejected_cleanly():
    response = client.post(
        "/sessions/00000000-0000-0000-0000-000000000000/chat",
        json={
            "message": "",
            "agent": "chat",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()
