import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def py_client():
    return TestClient(app)
