"""Controller for login-related requests."""

from typing import Any

from apps.services.authSvc import AuthService


class LoginController:
    """
    Controller for authentication-related requests.

    This controller sits between the Flask routes and AuthService.
    It extracts request data, validates required fields, and forwards
    valid requests to the service layer.
    """

    def __init__(self) -> None:
        """Create the auth service used for registration, login, and MFA."""
        self.auth_service = AuthService()

    def register_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an incoming registration request.

        Expected frontend JSON:
        {
            "username": "alice",
            "password": "password123",
            "role": "patient",
            "email": "example@email.com"
        }
        """
        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "").strip()
        email = data.get("email", "").strip()

        if not username:
            return {"status": "error", "message": "Username is required."}

        if not password:
            return {"status": "error", "message": "Password is required."}

        if not role:
            return {"status": "error", "message": "Role is required."}

        if not self._is_valid_email(email):
            return {
                "status": "error",
                "message": "A valid email is required for registration.",
            }

        return self.auth_service.register_user(
            username=username,
            password=password,
            role=role,
            email=email,
        )

    def login_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an incoming login request.

        Expected frontend JSON:
        {
            "username": "alice",
            "password": "password123",
            "role": "patient"
        }

        Email is not required during login because it is stored during
        registration and reused for MFA delivery.
        """
        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "").strip()

        if not username:
            return {"status": "error", "message": "Username is required."}

        if not password:
            return {"status": "error", "message": "Password is required."}

        if not role:
            return {"status": "error", "message": "Role is required."}

        return self.auth_service.authenticate(
            username=username,
            password=password,
            role=role,
        )

    def verify_mfa_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an incoming MFA verification request.

        Expected frontend JSON:
        {
            "username": "alice",
            "code": "654321"
        }
        """
        username = data.get("username", "").strip()
        code = data.get("code", "").strip()

        if not username:
            return {"status": "error", "message": "Username is required."}

        if not code:
            return {"status": "error", "message": "MFA code is required."}

        return self.auth_service.verify_mfa(username, code)

    def logout_request(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle logout requests.

        This currently returns a simple logout response.
        """
        username = data.get("username", "").strip()

        if not username:
            return {"status": "error", "message": "Username is required."}

        return {"status": "success", "message": f"{username} logged out."}

    def _is_valid_email(self, email: str) -> bool:
        """
        Check whether an email looks valid enough to send MFA.
        """
        return bool(email and "@" in email and "." in email.split("@")[-1])
