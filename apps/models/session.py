from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class Session:
    """
    Session model.

    This represents an authenticated session after the user successfully
    completes both password authentication and MFA verification.
    """
    session_id: str
    username: str
    created_at: datetime
    expires_at: datetime

    def is_valid(self) -> bool:
        """
        Return True if the session has not expired yet.
        """
        return datetime.now(timezone.utc) < self.expires_at

    @staticmethod
    def create_new(
        session_id: str,
        username: str,
        duration_minutes: int = 30,
    ) -> "Session":
        """
        Helper method for creating a new session with a default expiration time.
        """
        created = datetime.now(timezone.utc)
        expires = created + timedelta(minutes=duration_minutes)

        return Session(
            session_id=session_id,
            username=username,
            created_at=created,
            expires_at=expires,
        )
