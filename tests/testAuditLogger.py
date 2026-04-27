from app.services.audit_logger import AuditLogger


def test_log_event_creates_event():
    """
    Logging an event should store it and return the created event object.
    """
    logger = AuditLogger()
    event = logger.log_event("login_success", "alice", "success")

    assert event.event_type == "login_success"
    assert event.username == "alice"
    assert event.status == "success"


def test_get_all_events_returns_logged_items():
    """
    After logging events, get_all_events should return them.
    """
    logger = AuditLogger()
    logger.log_event("login_success", "alice", "success")
    logger.log_event("record_access", "alice", "success")

    events = logger.get_all_events()
    assert len(events) == 2
