from datetime import datetime
from apps.models.secEvent import SecurityEvent
from apps.repositories.auditRepo import AuditRepository


class AuditLogger:
    """
    Service responsible for recording security-related actions.

    This supports accountability by storing a trace of authentication
    activity, access attempts, and other sensitive operations.
    """
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuditLogger, cls).__new__(cls)
        return cls._instance
        
    def __init__(self) -> None:
        self.audit_repository = AuditRepository()
        self.next_event_id = 1

    def log_event(self, event_type: str, username: str, status: str) -> SecurityEvent:
        """
        Create and store a new security event.
        """
        event = SecurityEvent(
            event_id=self.next_event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            username=username,
            status=status,
        )
        self.audit_repository.save(event)
        self.next_event_id += 1
        return event

    def get_all_events(self):
        """
        Return every stored audit event.
        """
        return self.audit_repository.get_all()