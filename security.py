from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

passhasher = PasswordHasher()

def hash_password(password: str) -> str:
    return passhasher.hash(password)

def verify_password(password: str, hashed_pass: str) -> str:

    try:
        passhasher.verify(hashed_pass, password)
        return True
    except VerifyMismatchError:
        return False