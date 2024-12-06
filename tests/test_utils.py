# tests/test_utils.py

from app.utils import hash_password, check_password

def test_hash_password():
    """Test if the hash_password function hashes the password correctly"""
    password = "password123"
    hashed_password = hash_password(password)

    assert hashed_password != password  # The hashed password should not be the same
    assert hashed_password.startswith('$2b$')  # Check for bcrypt hash format

def test_check_password():
    """Test if the check_password function works correctly"""
    password = "password123"
    hashed_password = hash_password(password)

    assert check_password(hashed_password, password)  # Check if the password matches the hash
    assert not check_password(hashed_password, "wrongpassword")  # Should fail for incorrect password
