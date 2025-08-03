
import pytest
from app.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_shorten_valid_url(client):
    res = client.post("/api/shorten", json={"url": "https://example.com"})
    assert res.status_code == 200
    assert "short_code" in res.get_json()

def test_shorten_invalid_url(client):
    res = client.post("/api/shorten", json={"url": "invalid-url"})
    assert res.status_code == 400

def test_redirect_and_stats(client):
    res = client.post("/api/shorten", json={"url": "https://example.com"})
    short_code = res.get_json()["short_code"]

    # Redirect
    redirect_res = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_res.status_code == 302

    # Stats
    stats_res = client.get(f"/api/stats/{short_code}")
    stats_data = stats_res.get_json()
    assert stats_data["clicks"] == 1
    assert stats_data["url"] == "https://example.com"

def test_unknown_short_code(client):
    res = client.get("/api/stats/unknown123")
    assert res.status_code == 404
