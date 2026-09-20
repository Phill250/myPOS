from core.security import hash_password, verify_password

def test_hash_password():
    password = "testpassword"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password

def test_verify_password():
    password = "testpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("testpassword2", hashed)
     