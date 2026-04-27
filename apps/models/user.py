from dataclasses import dataclass


@dataclass
class User:
    """
    Simple user model.

    This dataclass represents a system user and stores the minimum information
    needed for authentication and authorization in the starter version.
    """
    user_id: int
    username: str
    password_hash: str
    email: str
    role: str
