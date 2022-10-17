"""
Implements all kind of hashing functionality.
"""
import binascii
import hashlib
import os


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pass_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                    salt, 100000)
    pass_hash = binascii.hexlify(pass_hash)
    return (salt + pass_hash).decode('ascii')


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pass_hash = hashlib.pbkdf2_hmac('sha512',
                                    provided_password.encode('utf-8'),
                                    salt.encode('ascii'),
                                    100000)
    pass_hash = binascii.hexlify(pass_hash).decode('ascii')
    return pass_hash == stored_password
