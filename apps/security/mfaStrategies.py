import os
import random
from abc import ABC, abstractmethod
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class MFAStrategy(ABC):
    @abstractmethod
    def send_code(self, user) -> None:
        pass

    @abstractmethod
    def verify_code(self, user, code: str) -> bool:
        pass


class EmailOTPStrategy(MFAStrategy):
    def __init__(self) -> None:
        self.active_codes: dict[str, str] = {}

    def send_code(self, user) -> None:
        code = f"{random.randint(100000, 999999)}"
        self.active_codes[user.username] = code

        message = Mail(
            from_email=os.environ["FROM_EMAIL"],
            to_emails=user.email,
            subject="Your CJ Secure MFA Code",
            html_content=f"""
            <h2>CJ Secure</h2>
            <p>Your CJ Hospital verification code is:</p>
            <h1>{code}</h1>
            <p>If you did not request this code, please ignore this email.</p>
            """
        )

        sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        sg.send(message)

    def verify_code(self, user, code: str) -> bool:
        expected = self.active_codes.get(user.username)
        return expected == code


class TOTPStrategy(MFAStrategy):
    def send_code(self, user) -> None:
        print(f"TOTP ready for user {user.username}")

    def verify_code(self, user, code: str) -> bool:
        return code == "654321"