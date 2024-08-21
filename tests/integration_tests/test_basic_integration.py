import pytest
from flask import Flask

@pytest.fixture
def client():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return 'Hello, World!'

    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello, World!' in response.data
