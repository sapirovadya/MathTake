import pytest
from flask import Flask, request, jsonify

@pytest.fixture
def client():
    app = Flask(__name__)

    # Mock database
    users = []

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.form
        new_user = {
            'name': data.get('name'),
            'email': data.get('email'),
            'password': data.get('password'),
            'role': data.get('role'),
            'phone': data.get('phone')
        }
        users.append(new_user)
        return jsonify(new_user), 201

    with app.test_client() as client:
        yield client

def test_signup(client):
    response = client.post('/signup', data={
        'name': 'Gaya',
        'email': 'gaya@example.com',
        'password': 'password123',
        'role': 'Student',
        'phone': '0501234567'
    })
    assert response.status_code == 201
    assert b'gaya@example.com' in response.data
