import pytest
import requests
from app import app
from app import generate_api_token

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.mark.integration
def test_search_endpoint_valid_token(client):
    url = "/search"
    token = generate_api_token()
    data = {"url": "https://example.com", "phrase": "example", "token": token}
    response = client.post(url, json=data)
    assert response.status_code == 200
    assert response.json()["found"] == True

@pytest.mark.integration
def test_search_endpoint_invalid_token(client):
    url = "/search"
    data = {"url": "https://example.com", "phrase": "example", "token": "invalid_token"}
    response = client.post(url, json=data)
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid API token"

@pytest.mark.integration
def test_search_endpoint_missing_token(client):
    url = "/search"
    data = {"url": "https://example.com", "phrase": "example"}
    response = client.post(url, json=data)
    assert response.status_code == 401
    assert response.json()["error"] == "API token is required"

@pytest.mark.integration
def test_search_endpoint_invalid_url(client):
    url = "/search"
    token = generate_api_token()
    data = {"url": "invalid_url", "phrase": "example", "token": token}
    response = client.post(url, json=data)
    assert response.status_code == 400
    assert response.json()["error"] == "Invalid URL"