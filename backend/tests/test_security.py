from security import hash_password, verify_password


def test_verify_password_accepts_correct_password():
    hashed = hash_password("correct-password")
    assert verify_password("correct-password", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("correct-password")
    assert verify_password("wrong-password", hashed) is False


def test_hash_password_does_not_store_plaintext():
    assert hash_password("correct-password") != "correct-password"


def test_hash_password_uses_a_random_salt():
    assert hash_password("same-password") != hash_password("same-password")
