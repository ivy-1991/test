from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def token():
    r = client.post("/api/auth/login", json={"username": settings.admin_username, "password": settings.admin_password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_auth_rejects_bad_password():
    assert client.post("/api/auth/login", json={"username": "admin", "password": "bad"}).status_code == 401


def test_status_requires_auth_and_returns_metrics():
    assert client.get("/api/system/status").status_code in {401, 403}
    r = client.get("/api/system/status", headers={"Authorization": f"Bearer {token()}"})
    assert r.status_code == 200
    assert "storage_free_bytes" in r.json()
