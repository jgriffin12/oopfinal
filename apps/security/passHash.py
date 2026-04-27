import hashlib


class PasswordHasher:
    """
    Utility class for hashing and verifying passwords.

    This starter version uses SHA-256 only for demonstration purposes.
    In a production system, a stronger password-specific algorithm such as
    bcrypt, scrypt, or Argon2 should be used instead.
    """

    def hash_password(self, password: str) -> str:
        """
        Hash a plain-text password and return the hex digest.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Compare the hash of the submitted password against the stored hash.
        """
        return self.hash_password(password) == stored_hash
