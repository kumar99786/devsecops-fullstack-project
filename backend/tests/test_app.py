import pytest
from backend.app import app
from unittest.mock import patch

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Backend is running!" in response.data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert b"OK" in response.data


def test_services(client):
    response = client.get("/api/services")
    assert response.status_code == 200
    assert b"DevOps Automation" in response.data


@patch("app.get_db_connection")
def test_contact(mock_db, client):
    mock_conn = mock_db.return_value
    mock_cursor = mock_conn.cursor.return_value

    response = client.post(
        "/api/contact",
        json={
            "name": "Test",
            "email": "test@example.com",
            "message": "Hello"
        }
    )

    assert response.status_code == 201
    assert b"Contact saved successfully" in response.data

