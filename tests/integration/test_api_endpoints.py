from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "AuraCode" in response.text
    assert "text/html" in response.headers["content-type"]


def test_get_aura_svg():
    response = client.get("/api/aura/octocat.svg")
    assert response.status_code == 200
    assert "image/svg+xml" in response.headers["content-type"]
    assert "AURACODE // DEV SPOTIFY WRAPPED" in response.text

def test_get_user_aura_profile():
    response = client.get("/api/aura/octocat")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "octocat"
    assert -5000 <= data["aura_score"] <= 10000
    assert "archetype" in data
    assert "roast_commentary" in data
    assert len(data["version_hash"]) > 0

