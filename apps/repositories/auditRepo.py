from typing import List
from apps.models.secEvent import SecurityEvent


class AuditRepository:
    """
    Repository responsible for storing audit events.

    This starter version keeps audit events in memory. Later, these events
    can be stored in a database or secure logging system.
    """

    def __init__(self) -> None:
        self.events: List[SecurityEvent] = []

    def save(self, event: SecurityEvent) -> None:
        """
        Store a security event in the in-memory list.
        """
        self.events.append(event)

    def get_all(self) -> List[SecurityEvent]:
        """
        Return all stored audit events.
        """
        return self.events
