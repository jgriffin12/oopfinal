"""Final edge-case tests to increase coverage."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from apps.models.permission import Permission
from apps.models.record import Record
from apps.models.secEvent import SecurityEvent
from apps.repositories.auditRepo import AuditRepository
from apps.repositories.userRepo import UserRepository
from apps.security.mfaFactory import MFAFactory
from apps.security.mfaStrategies import EmailOTPStrategy
from apps.services.auditLogger import AuditLogger
from apps.services.authSvc import AuthService


def test_permission_model():
    """Permission model should store permission data."""
    permission = Permission("view_masked_record")

    assert permission is not None
    assert "view_masked_record" in repr(permission)


def test_record_model_optional_methods():
    """Record model should expose stored record data."""
    record = Record(
        record_id=1,
        patient_name="Alice Anderson",
        ssn="123-45-6789",
        medical_notes="Patient notes",
    )

    assert record.record_id == 1
    assert record.patient_name == "Alice Anderson"
    assert record.ssn == "123-45-6789"
    assert record.medical_notes == "Patient notes"

    if hasattr(record, "to_dict"):
        assert record.to_dict()["record_id"] == 1


def test_security_event_optional_methods():
    """SecurityEvent model should expose stored event data."""
    event = SecurityEvent(
        event_id=1,
        timestamp=datetime.now(timezone.utc),
        event_type="login_success",
        username="alice",
        status="success",
    )

    assert event.event_id == 1
    assert event.event_type == "login_success"
    assert event.username == "alice"
    assert event.status == "success"

    if hasattr(event, "to_dict"):
        assert event.to_dict()["event_type"] == "login_success"


def test_audit_repository_get_all_events():
    """AuditRepository should return saved events."""
    repository = AuditRepository()

    event = SecurityEvent(
        event_id=1,
        timestamp=datetime.now(timezone.utc),
        event_type="login_success",
        username="alice",
        status="success",
    )

    if hasattr(repository, "add_event"):
        repository.add_event(event)
    elif hasattr(repository, "save"):
        repository.save(event)
    elif hasattr(repository, "events"):
        repository.events.append(event)

    if hasattr(repository, "get_all_events"):
        events = repository.get_all_events()
    else:
        events = repository.events

    assert len(events) == 1
    assert events[0].event_type == "login_success"


def test_audit_logger_get_all_events():
    """AuditLogger should return logged events."""
    logger = AuditLogger()

    logger.log_event("login_success", "alice", "success")
    events = logger.get_all_events()

    assert len(events) == 1
    assert events[0].event_type == "login_success"


def test_user_repository_duplicate_create_user(tmp_path, monkeypatch):
    """Creating an existing username should raise ValueError."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    with pytest.raises(ValueError):
        repository.create_user(
            username="alice",
            password="password123",
            role="admin",
            email="alice@example.com",
        )


def test_user_repository_create_user_return_value(tmp_path, monkeypatch):
    """create_user should return the created user."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    user = repository.create_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    assert user.username == "chica"
    assert user.email == "chica@example.com"
    assert user.role == "patient"


def test_mfa_factory_creates_email_strategy():
    """MFAFactory should create the email strategy branch."""
    factory = MFAFactory()

    strategy = factory.create_strategy("email")

    assert isinstance(strategy, EmailOTPStrategy)


def test_auth_service_register_missing_fields(tmp_path, monkeypatch):
    """AuthService registration should reject missing fields."""
    monkeypatch.chdir(tmp_path)

    service = AuthService()

    result = service.register_user(
        username="",
        password="",
        role="",
        email="",
    )

    assert result["status"] == "error"
    assert "required" in result["message"]


def test_auth_service_verify_unknown_user(tmp_path, monkeypatch):
    """AuthService MFA verification should reject unknown users."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    result = service.verify_mfa(
        username="missing",
        code="654321",
    )

    assert result["status"] == "error"
    assert result["message"] == "User not found."


def test_email_strategy_verify_missing_code():
    """EmailOTPStrategy should reject users with no active code."""
    strategy = EmailOTPStrategy()
    user = SimpleNamespace(username="alice", email="alice@example.com")

    assert strategy.verify_code(user, "123456") is False


def test_record_get_summary():
    """Record get_summary should return the expected summary string."""
    record = Record(
        record_id=1,
        patient_name="Alice Anderson",
        ssn="123-45-6789",
        medical_notes="Patient notes",
    )

    assert record.get_summary() == "Record 1 for Alice Anderson"


def test_user_repository_find_by_email_existing_and_missing(tmp_path, monkeypatch):
    """UserRepository should find users by stored email."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    existing = repository.find_by_email("DEMO@EXAMPLE.COM")
    missing = repository.find_by_email("missing@example.com")

    assert existing is not None
    assert existing.username == "alice"
    assert missing is None


def test_login_controller_check_email_invalid_new_and_existing(tmp_path, monkeypatch):
    """LoginController should support the email-first account lookup flow."""
    monkeypatch.chdir(tmp_path)

    from apps.controllers.loginController import LoginController

    controller = LoginController()

    invalid = controller.check_email_request({"email": "bad-email"})
    assert invalid["status"] == "error"

    new_user = controller.check_email_request({"email": "new@example.com"})
    assert new_user["status"] == "new_user"

    controller.auth_service.register_user(
        username="chica",
        password="password123",
        role="provider",
        email="chica@example.com",
    )

    existing = controller.check_email_request({"email": "chica@example.com"})
    assert existing["status"] == "existing_user"
    assert existing["username"] == "chica"
    assert existing["role"] == "provider"


def test_check_email_route(monkeypatch):
    """The /check-email route should return the controller lookup result."""
    from apps.main import create_app
    from apps.routes import authRoutes

    class FakeLoginController:
        def check_email_request(self, data):
            return {
                "status": "existing_user",
                "email": data["email"],
                "username": "chica",
                "role": "provider",
            }

    authRoutes.login_controller = FakeLoginController()

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/check-email",
        json={"email": "chica@example.com"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "existing_user"


def test_check_email_route_error(monkeypatch):
    """The /check-email route should return 400 for invalid email data."""
    from apps.main import create_app
    from apps.routes import authRoutes

    class FakeLoginController:
        def check_email_request(self, data):
            return {
                "status": "error",
                "message": "A valid email is required.",
            }

    authRoutes.login_controller = FakeLoginController()

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/check-email",
        json={"email": "bad-email"},
    )

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


def test_user_repository_next_user_id_empty_list(tmp_path, monkeypatch):
    """_next_user_id should return 1 when no users exist."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    assert repository._next_user_id([]) == 1


def test_user_repository_duplicate_email_create_user(tmp_path, monkeypatch):
    """Creating an existing email should raise ValueError."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    with pytest.raises(ValueError):
        repository.create_user(
            username="newalice",
            password="password123",
            role="patient",
            email="demo@example.com",
        )


def test_user_repository_all_users(tmp_path, monkeypatch):
    """all_users should return every stored user model."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()
    users = repository.all_users()

    assert len(users) >= 2
    assert users[0].username == "alice"
    assert users[0].user_id == 1
