# tests/test_models.py

from app import db
from app.models import User

def test_create_user():
    """Test creating a new user in the database"""
    user = User(username="testuser", email="test@example.com", password="password123")
    db.session.add(user)
    db.session.commit()

    # Check if the user is added to the database
    retrieved_user = User.query.filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"

def test_user_password_hashing():
    """Test if the password is hashed correctly"""
    user = User(username="testuser", email="test@example.com", password="password123")
    db.session.add(user)
    db.session.commit()

    retrieved_user = User.query.filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.password != "password123"  # The password should be hashed
    assert retrieved_user.password.startswith('$2b$')  # bcrypt hash format check

def test_delete_user():
    """Test deleting a user from the database"""
    user = User(username="testuser", email="test@example.com", password="password123")
    db.session.add(user)
    db.session.commit()

    user_to_delete = User.query.filter_by(username="testuser").first()
    db.session.delete(user_to_delete)
    db.session.commit()

    deleted_user = User.query.filter_by(username="testuser").first()
    assert deleted_user is None  # User should be deleted
