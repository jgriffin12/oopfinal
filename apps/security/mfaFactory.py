from apps.security.mfaStrategies import EmailOTPStrategy, TOTPStrategy, MFAStrategy


class MFAFactory:
    """
    Factory responsible for creating the correct MFA strategy object.
    """

    _email_strategy = EmailOTPStrategy()
    _totp_strategy = TOTPStrategy()

    def create_strategy(self, method: str) -> MFAStrategy:
        if method == "email":
            return self._email_strategy

        if method == "totp":
            return self._totp_strategy

        raise ValueError(f"Unsupported MFA method: {method}")