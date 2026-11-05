
from unittest.mock import MagicMock

import app as url_app
import pytest


@pytest.fixture
def client():
    url_app.app.config["TESTING"] = True
    return url_app.app.test_client()


def mock_database(monkeypatch, fetchone=None):
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone

    conn.__enter__.return_value = conn
    conn.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(url_app, "get_connection", lambda: conn)

    return conn, cursor


def test_shorten_valid_url(client, monkeypatch):
    mock_database(monkeypatch)
    monkeypatch.setattr(url_app.cache, "setex", MagicMock())

    response = client.post(
        "/shorten",
        json={"url": "https://github.com"}
    )

    assert response.status_code == 201
    assert response.json["original_url"] == "https://github.com"
    assert response.json["short_code"]


def test_shorten_rejects_invalid_url(client):
    response = client.post(
        "/shorten",
        json={"url": "not-a-valid-url"}
    )

    assert response.status_code == 400


def test_shorten_requires_url(client):
    response = client.post("/shorten", json={})

    assert response.status_code == 400


def test_redirect_uses_cache(client, monkeypatch):
    monkeypatch.setattr(
        url_app.cache,
        "get",
        lambda code: "https://github.com"
    )

    response = client.get("/abc123")

    assert response.status_code == 302
    assert response.location == "https://github.com"


def test_redirect_uses_database_on_cache_miss(client, monkeypatch):
    mock_database(monkeypatch, fetchone=("https://github.com",))

    monkeypatch.setattr(url_app.cache, "get", lambda code: None)
    monkeypatch.setattr(url_app.cache, "setex", MagicMock())

    response = client.get("/abc123")

    assert response.status_code == 302
    assert response.location == "https://github.com"
