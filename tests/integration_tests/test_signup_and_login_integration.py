import pytest
from flask import Flask, request, jsonify, session

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'

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

    @app.route('/login', methods=['POST'])
    def login():
        data = request.form
        user = next((u for u in users if u['email'] == data.get('email') and u['password'] == data.get('password')), None)
        if user:
            session['user'] = user
            return jsonify({"message": "Login successful"}), 200
        return jsonify({"message": "Invalid credentials"}), 401

    with app.test_client() as client:
        yield client

def test_signup_and_login(client):
    # Signup
    signup_response = client.post('/signup', data={
        'name': 'Gaya',
        'email': 'gaya@example.com',
        'password': 'password123',
        'role': 'Student',
        'phone': '0501234567'
    })
    assert signup_response.status_code == 201
    assert b'gaya@example.com' in signup_response.data

    # Login
    login_response = client.post('/login', data={
        'email': 'gaya@example.com',
        'password': 'password123'
    })
    assert login_response.status_code == 200
    assert b'Login successful' in login_response.data
