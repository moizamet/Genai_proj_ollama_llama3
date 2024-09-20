import pytest
import json
from app import app  

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"Message": "Success"}

def test_add_book(client):
    """Test adding a new book."""
    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "genre": "Fiction",
        "year_published": 2023,
        "content": "This is a test book content."
    }

    # Use basic auth for the test
    response = client.post('/books',
                           data=json.dumps(new_book),
                           content_type='application/json',
                           headers={"Authorization": "Basic bW9pemFtZXQ6MSM1MlN1Y2NlcyQ="})  

    assert response.status_code == 201
    assert "Record Inserted Successfully" in response.json["Message"]

