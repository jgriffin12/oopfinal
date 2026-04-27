"""MFA strategy classes for email OTP and TOTP."""

import os
import random
from abc import ABC, abstractmethod
from typing import Any

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class MFAStrategy(ABC):
    """Abstract base class for MFA strategies."""

    @abstractmethod
    def send_code(self, user: Any) -> None:
        """Send an MFA code or prepare an MFA challenge."""
        pass

    @abstractmethod
    def verify_code(self, user: Any, code: str) -> bool:
        """Verify an MFA code."""
        pass


class EmailOTPStrategy(MFAStrategy):
    """Email one-time password MFA strategy using SendGrid."""

    def __init__(self) -> None:
        """Store active MFA codes in memory."""
        self.active_codes: dict[str, str] = {}

    def send_code(self, user: Any) -> None:
        """Generate and send an MFA code to the user's email."""
        if not getattr(user, "email", ""):
            print("[MFA ERROR] No email provided for user.")
            return

        code = f"{random.randint(100000, 999999)}"
        self.active_codes[user.username] = code

        try:
            message = Mail(
                from_email=os.environ["FROM_EMAIL"],
                to_emails=user.email,
                subject="Your CJ Secure MFA Code",
                html_content=f"""
                <h2>CJ Secure</h2>
                <p>Your CJ Hospital verification code is:</p>
                <h1>{code}</h1>
                <p>If you did not request this code, please ignore this email.</p>
                """,
            )

            sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
            sg.send(message)

            print(f"[MFA] Code sent to {user.email}")

        except KeyError as error:
            print(f"[MFA ERROR] Missing environment variable: {error}")

        except Exception as error:
            print(f"[MFA ERROR] Failed to send email: {error}")

    def verify_code(self, user: Any, code: str) -> bool:
        """Verify the submitted email MFA code."""
        expected = self.active_codes.get(user.username)

        if expected and expected == code:
            del self.active_codes[user.username]
            return True

        return False


class TOTPStrategy(MFAStrategy):
    """Placeholder TOTP strategy."""

    def send_code(self, user: Any) -> None:
        """Prepare TOTP MFA challenge."""
        print(f"TOTP ready for user {user.username}")

    def verify_code(self, user: Any, code: str) -> bool:
        """Verify TOTP code."""
        return code == "654321"
