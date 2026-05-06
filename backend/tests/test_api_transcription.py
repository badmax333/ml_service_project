from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_list_models():
    response = client.get("/transcribe/models")
    assert response.status_code == 200
    assert len(response.json()) == 3