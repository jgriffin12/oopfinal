"""User repository for storing and retrieving portal users."""

import json
from pathlib import Path

from apps.models.user import User
from apps.security.passHash import PasswordHasher


class UserRepository:
    """
    Repository responsible for user data access.

    For this class project, users are stored in a local JSON file.
    In a real healthcare system, this would be replaced with a secure database.
    """

    def __init__(self) -> None:
        """Load users from local storage or create a default demo user."""
        self.password_hasher = PasswordHasher()
        self.data_path = Path("data/users.json")
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.users = self._load_users()

        if not self.users:
            self.users = {
                "alice": User(
                    user_id=1,
                    username="alice",
                    password_hash=self.password_hasher.hash_password("password123"),
                    email="demo@example.com",
                    role="admin",
                )}
            self._save_users()

    def _load_users(self) -> dict[str, User]:
        """
        Load users from the local JSON file.

        If the file does not exist, return an empty dictionary.
        """
        if not self.data_path.exists():
            return {}

        with self.data_path.open("r", encoding="utf-8") as file:
            raw_users = json.load(file)

        users = {}

        for username, data in raw_users.items():
            users[username] = User(
                user_id=data["user_id"],
                username=data["username"],
                password_hash=data["password_hash"],
                email=data["email"],
                role=data["role"],
            )

        return users

    def _save_users(self) -> None:
        """
        Save all users to the local JSON file.
        """
        raw_users = {}

        for username, user in self.users.items():
            raw_users[username] = {
                "user_id": user.user_id,
                "username": user.username,
                "password_hash": user.password_hash,
                "email": user.email,
                "role": user.role,
            }

        with self.data_path.open("w", encoding="utf-8") as file:
            json.dump(raw_users, file, indent=2)

    def find_by_username(self, username: str) -> User | None:
        """
        Find a user by username.

        Returns None when the username does not exist.
        """
        return self.users.get(username)

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
    ) -> User:
        """
        Create and store a new user.

        The email is provided once during registration and then stored
        for future MFA delivery.
        """
        if username in self.users:
            raise ValueError("Username already exists.")

        next_user_id = len(self.users) + 1

        user = User(
            user_id=next_user_id,
            username=username,
            password_hash=self.password_hasher.hash_password(password),
            email=email,
            role=role,
        )

        self.users[username] = user
        self._save_users()

        return user
