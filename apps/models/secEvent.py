from dataclasses import dataclass
from datetime import datetime


@dataclass
class SecurityEvent:
    """
    Security event model.

    Audit logging records important actions in the system so there is a
    trace of what happened, when it happened, and whether it succeeded.
    """
    event_id: int
    timestamp: datetime
    event_type: str
    username: str
    status: str

    def to_dict(self) -> dict:
        """
        Convert the event into a dictionary so it can be serialized or returned
        in a response if needed.
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "username": self.username,
            "status": self.status,
        }
