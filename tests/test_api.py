import importlib
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp.close()
    monkeypatch.setenv("DB_PATH", tmp.name)

    import backend.main as main_module

    main_module = importlib.reload(main_module)

    fake_meta = {
        "title": "Mocked Title",
        "description": "Mocked description",
        "image": "https://example.com/cover.jpg",
        "site_name": "Mocked Site",
        "author": "Tester",
        "canonical_url": "https://example.com/canonical",
        "fetch_status": "ok",
    }
    monkeypatch.setattr(main_module, "extract_metadata", lambda url: dict(fake_meta))

    with TestClient(main_module.app) as test_client:
        yield test_client

    try:
        os.unlink(tmp.name)
    except OSError:
        pass


def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_item_success(client):
    response = client.post("/items", json={"url": "https://example.com/article"})
    assert response.status_code == 201
    body = response.json()
    assert body["url"] == "https://example.com/article"
    assert body["title"] == "Mocked Title"
    assert body["fetch_status"] == "ok"
    assert body["id"]
    assert body["created_at"].endswith("Z")


def test_create_item_invalid_scheme(client):
    response = client.post("/items", json={"url": "ftp://example.com/file"})
    assert response.status_code == 422
    assert "http" in response.json()["detail"].lower()


def test_create_item_empty_string(client):
    response = client.post("/items", json={"url": "   "})
    assert response.status_code == 422
    assert "empty" in response.json()["detail"].lower()


def test_create_item_missing_field(client):
    response = client.post("/items", json={})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_list_items_returns_newest_first(client, monkeypatch):
    import backend.main as main_module

    statuses = ["ok", "partial", "failed"]
    for i, status in enumerate(statuses):
        monkeypatch.setattr(
            main_module,
            "extract_metadata",
            lambda url, _s=status: {
                "title": f"Title {_s}" if _s != "partial" else None,
                "description": None,
                "image": None,
                "site_name": None,
                "author": None,
                "canonical_url": None,
                "fetch_status": _s,
            },
        )
        response = client.post(
            "/items", json={"url": f"https://example.com/{i}"}
        )
        assert response.status_code == 201

    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3

    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True)


def test_failed_fetch_still_persists(client, monkeypatch):
    import backend.main as main_module

    monkeypatch.setattr(
        main_module,
        "extract_metadata",
        lambda url: {
            "title": None,
            "description": None,
            "image": None,
            "site_name": None,
            "author": None,
            "canonical_url": None,
            "fetch_status": "failed",
        },
    )
    response = client.post("/items", json={"url": "https://unreachable.example/"})
    assert response.status_code == 201
    body = response.json()
    assert body["fetch_status"] == "failed"
    assert body["title"] is None
