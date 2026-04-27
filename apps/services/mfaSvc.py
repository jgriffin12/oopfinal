"""Service for coordinating MFA operations."""

from apps.security.mfaFactory import MFAFactory


class MFAService:
    """
    Service responsible for coordinating MFA operations.

    AuthService asks this service to send or verify MFA codes.
    MFAService uses MFAFactory to create the correct MFA strategy.
    """

    def __init__(self) -> None:
        """Create the MFA factory."""
        self.mfa_factory = MFAFactory()

    def send_mfa_code(self, user, method: str = "email") -> None:
        """
        Send an MFA code using the requested MFA method.
        """
        strategy = self.mfa_factory.create_strategy(method)
        strategy.send_code(user)

    def verify_mfa_code(self, user, code: str, method: str = "email") -> bool:
        """
        Verify an MFA code using the requested MFA method.
        """
        strategy = self.mfa_factory.create_strategy(method)
        return strategy.verify_code(user, code)
