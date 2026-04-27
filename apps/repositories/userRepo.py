"""Repository for storing and loading user profiles."""

import json
from pathlib import Path
from typing import Any

from apps.models.user import User
from apps.security.passHash import PasswordHasher


class UserRepository:
    """
    Repository for user profiles.

    Users are stored in a JSON text file so registered providers and patients
    persist after the app restarts.
    """

    def __init__(self, file_path: str = "data/users.json") -> None:
        """Create the repository and ensure the storage file exists."""
        self.file_path = Path(file_path)
        self.password_hasher = PasswordHasher()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_seed_users()

    def _ensure_seed_users(self) -> None:
        """
        Create the user file with demo users if it does not exist.

        This keeps the original demo accounts working while also supporting
        newly registered users.
        """
        if self.file_path.exists():
            return

        seed_users = [
            {
                "user_id": 1,
                "username": "alice",
                "email": "demo@example.com",
                "role": "provider",
                "password_hash": self.password_hasher.hash_password(
                    "password123"
                ),
            },
            {
                "user_id": 2,
                "username": "bob",
                "email": "bob@example.com",
                "role": "patient",
                "password_hash": self.password_hasher.hash_password(
                    "password123"
                ),
            },
        ]

        self._write_users(seed_users)

    def _read_users(self) -> list[dict[str, Any]]:
        """Read all users from the JSON text file."""
        with self.file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    def _write_users(self, users: list[dict[str, Any]]) -> None:
        """Write all users to the JSON text file."""
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)

    def _next_user_id(self, users: list[dict[str, Any]]) -> int:
        """Return the next available integer user ID."""
        if not users:
            return 1

        return max(int(user_data.get("user_id", 0)) for user_data in users) + 1

    def _to_user(self, data: dict[str, Any]) -> User:
        """Convert stored dictionary data into a User model."""
        return User(
            user_id=int(data["user_id"]),
            username=str(data["username"]),
            password_hash=str(data["password_hash"]),
            role=str(data["role"]),
            email=str(data["email"]),
        )

    def find_by_username(self, username: str) -> User | None:
        """Find a user by username."""
        normalized_username = username.strip().lower()

        for user_data in self._read_users():
            stored_username = str(user_data["username"]).strip().lower()
            if stored_username == normalized_username:
                return self._to_user(user_data)

        return None

    def find_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        normalized_email = email.strip().lower()

        for user_data in self._read_users():
            stored_email = str(user_data["email"]).strip().lower()
            if stored_email == normalized_email:
                return self._to_user(user_data)

        return None

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
    ) -> User:
        """
        Create and persist a new user profile.

        Duplicate usernames or emails are rejected.
        """
        if self.find_by_username(username) is not None:
            raise ValueError("Username already exists.")

        if self.find_by_email(email) is not None:
            raise ValueError("Email already exists.")

        users = self._read_users()

        user = User(
            user_id=self._next_user_id(users),
            username=username.strip(),
            password_hash=self.password_hasher.hash_password(password),
            role=role.strip().lower(),
            email=email.strip().lower(),
        )

        users.append(
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "password_hash": user.password_hash,
            }
        )
        self._write_users(users)

        return user

    def all_users(self) -> list[User]:
        """Return all stored users."""
        return [self._to_user(user_data) for user_data in self._read_users()]
