import hashlib


class Tokenizer:
    """
    Utility class for tokenizing sensitive data.

    Tokenization replaces the visible value with a derived token. In a real
    system, tokenization is often handled with more advanced secure mapping
    or vault-based techniques.
    """

    def tokenize(self, value: str) -> str:
        """
        Return a short token based on a SHA-256 hash of the input value.

        This is a simplified classroom-friendly version.
        """
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"TOKEN-{digest[:12]}"
