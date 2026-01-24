from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_presets_endpoint_returns_200_and_list():
    response = client.get("/api/v1/presets/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert data, "Список пресетов не должен быть пустым"


def test_presets_endpoint_contains_misis_preset():
    response = client.get("/api/v1/presets/")
    assert response.status_code == 200

    data = response.json()
    ids = {item["id"] for item in data}
    assert "misis_v1" in ids

    misis = next(item for item in data if item["id"] == "misis_v1")
    assert misis["title"]
    assert misis.get("is_default") is True
