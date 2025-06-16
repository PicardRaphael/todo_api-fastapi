"""
Password Service for the Todo API.

This service handles password hashing and verification
using bcrypt for secure password storage.
"""

import bcrypt


class PasswordService:
    """
    Service for handling password operations.

    Provides secure password hashing and verification using bcrypt.
    """

    def __init__(self):
        """Initialize password service."""
        self.salt_rounds = 12  # Strong salt rounds for bcrypt

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password (str): Plain text password

        Returns:
            str: Hashed password
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password (str): Plain text password to verify
            hashed_password (str): Stored hashed password

        Returns:
            bool: True if password matches, False otherwise
        """
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
