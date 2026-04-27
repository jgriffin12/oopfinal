"""Authentication service for registration, login, and MFA."""

import os
from typing import Any

from apps.repositories.userRepo import UserRepository
from apps.security.passHash import PasswordHasher
from apps.services.mfaSvc import MFAService


class AuthService:
    """
    Service responsible for authentication.

    This class handles one-time user registration, username/password login,
    MFA code delivery, and MFA verification.
    """

    def __init__(self) -> None:
        """Create the dependencies needed for authentication."""
        self.user_repository = UserRepository()
        self.password_hasher = PasswordHasher()
        self.mfa_service = MFAService()

    def _get_mfa_method(self) -> str:
        """
        Read the MFA method from the environment.

        Default is email for the real SendGrid workflow.
        For testing and demo reliability, use MFA_METHOD=totp.
        """
        return os.getenv("MFA_METHOD", "email").strip().lower() or "email"

    def register_user(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
    ) -> dict[str, Any]:
        """
        Register a user one time.

        The user provides their email during registration. After that,
        login only needs username, password, and role. The stored email
        is used later for MFA delivery.
        """
        if not username or not password or not role or not email:
            return {
                "status": "error",
                "message": "Username, password, role, and email are required.",
            }

        existing_user = self.user_repository.find_by_username(username)

        if existing_user is not None:
            return {
                "status": "error",
                "message": "Username already exists.",
            }

        self.user_repository.create_user(
            username=username,
            password=password,
            role=role,
            email=email,
        )

        return {
            "status": "success",
            "message": "Account created. You can now log in.",
            "username": username,
            "role": role,
        }

    def authenticate(
        self,
        username: str,
        password: str,
        role: str,
    ) -> dict[str, Any]:
        """
        Authenticate a user and send an MFA code.

        The email is not entered during login. It is pulled from the stored
        user account that was created during registration.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {
                "status": "error",
                "message": "Invalid username or password.",
            }

        if user.role != role:
            return {
                "status": "error",
                "message": "Selected role does not match this user.",
            }

        if not self.password_hasher.verify_password(
                password, user.password_hash):
            return {
                "status": "error",
                "message": "Invalid username or password.",
            }

        method = self._get_mfa_method()
        self.mfa_service.send_mfa_code(user, method)

        return {
            "status": "pending",
            "message": f"Login successful. MFA code sent using {method}.",
            "username": username,
            "role": role,
        }

    def verify_mfa(self, username: str, code: str) -> dict[str, Any]:
        """
        Verify the MFA code entered by the user.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {
                "status": "error",
                "message": "User not found.",
            }

        method = self._get_mfa_method()
        verified = self.mfa_service.verify_mfa_code(user, code, method)

        if not verified:
            return {
                "status": "error",
                "message": "Invalid MFA code.",
            }

        return {
            "status": "success",
            "message": "MFA verified. Login complete.",
            "username": username,
            "role": user.role,
        }
