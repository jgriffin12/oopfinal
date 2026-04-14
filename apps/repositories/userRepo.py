from apps.models.user import User
from apps.security.passHash import PasswordHasher


class UserRepository:
    """
    Repository responsible for user data access.
    """

    def __init__(self) -> None:
        hasher = PasswordHasher()

        self.users = {
            "alice": User(
                user_id=1,
                username="alice",
                password_hash=hasher.hash_password("password123"),
                email="lia03gomes@gmail.com",
                role="admin",
            )
        }

    def find_by_username(self, username: str):
        """
        Return a User object if the username exists.
        """
        return self.users.get(username)