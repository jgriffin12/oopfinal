from datetime import datetime
from apps.models.secEvent import SecurityEvent
from apps.repositories.auditRepo import AuditRepository


class AuditLogger:
    """
    Singleton service responsible for recording security-related actions.

    This ensures the application uses one shared audit logger so audit
    events are collected in a single place across the system.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """
        Ensure only one AuditLogger instance is ever created.
        """
        if cls._instance is None:
            cls._instance = super(AuditLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the singleton only once.

        Without this guard, every call to AuditLogger() would reset the
        repository and event counter.
        """
        if self.__class__._initialized:
            return

        self.audit_repository = AuditRepository()
        self.next_event_id = 1
        self.__class__._initialized = True

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