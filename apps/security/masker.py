class SensitiveDataMasker:
    """
    Utility class for masking sensitive values before they are displayed.

    Masking allows the system to show only part of a value, which helps
    protect confidentiality while still allowing limited identification.
    """

    def mask_ssn(self, ssn: str) -> str:
        """
        Mask all but the last four digits of an SSN-like value.

        Example:
        123-45-6789 -> ***-**-6789
        """
        if len(ssn) < 4:
            return "****"
        return f"***-**-{ssn[-4:]}"

    def mask_name(self, name: str) -> str:
        """
        Partially mask a person's name.

        Example:
        Alice -> A****
        """
        if not name:
            return ""
        return name[0] + "*" * (len(name) - 1)
