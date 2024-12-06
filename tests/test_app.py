# tests/test_app.py

import pytest
from app import create_app, db
from app.models import User
from flask_login import login_user

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SECRET_KEY'] = 'testsecretkey'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create all tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests

def test_home(client):
    """Test the home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to Safehaven" in response.data

def test_register(client):
    """Test the registration page"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data

    # Test successful registration
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert b"Your account has been created!" in response.data

def test_login(client):
    """Test the login page"""
    user = User(username="testuser", email="test@example.com", password="password123")
    db.session.add(user)
    db.session.commit()

    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

    # Test successful login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert b"You have been logged in!" in response.data

def test_dashboard(client):
    """Test the dashboard page (requires login)"""
    user = User(username="testuser", email="test@example.com", password="password123")
    db.session.add(user)
    db.session.commit()

    login_user(user)
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Dashboard" in response.data
