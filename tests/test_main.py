from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def list_books():
    endpoint = "/books/"
    response = client.get(endpoint)
    

    assert response.status_code == 200
    