"""Tests for controllers, routes, models, and MFA strategies."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from apps.controllers.adminController import AdminController
from apps.controllers.loginController import LoginController
from apps.controllers.recordController import RecordController
from apps.main import create_app
from apps.models.role import Role
from apps.models.session import Session
from apps.security.mfaStrategies import EmailOTPStrategy, MFAStrategy, TOTPStrategy


class FakeAuthService:
    """Fake auth service used to isolate LoginController tests."""

    def register_user(self, username, password, role, email):
        return {
            "status": "success",
            "username": username,
            "role": role,
            "email": email,
        }

    def authenticate(self, username, password, role):
        return {
            "status": "pending",
            "username": username,
            "role": role,
        }

    def verify_mfa(self, username, code):
        return {
            "status": "success",
            "username": username,
            "code": code,
        }


class FakeUserRepository:
    """Fake user repository for controller tests."""

    def __init__(self, user=None):
        self.user = user

    def find_by_username(self, username):
        return self.user


class FakeAccessControlService:
    """Fake access control service for admin controller tests."""

    def __init__(self, authorized):
        self.authorized = authorized

    def is_authorized(self, user, permission):
        return self.authorized


class FakeAuditLogger:
    """Fake audit logger for admin controller tests."""

    def __init__(self):
        self.logged = []
        self.events = [
            SimpleNamespace(
                event_id=1,
                timestamp=datetime.now(timezone.utc),
                event_type="login_success",
                username="alice",
                status="success",
            )
        ]

    def log_event(self, event_type, username, status):
        self.logged.append((event_type, username, status))

    def get_all_events(self):
        return self.events


class FakeRecordService:
    """Fake record service for record controller tests."""

    def get_masked_record(self, user, record_id):
        return {
            "status": "success",
            "record": {
                "record_id": record_id,
                "patient_name": "A****",
            },
        }


class DummyMFAStrategy(MFAStrategy):
    """Concrete strategy to cover the abstract parent methods."""

    def send_code(self, user):
        return super().send_code(user)

    def verify_code(self, user, code):
        return super().verify_code(user, code)


def test_login_controller_register_validation():
    controller = LoginController()

    assert controller.register_request(
        {})["message"] == "Username is required."
    assert controller.register_request({"username": "a"})[
        "message"] == "Password is required."
    assert controller.register_request({"username": "a", "password": "p"})[
        "message"] == "Role is required."

    result = controller.register_request(
        {"username": "a", "password": "p", "role": "patient", "email": "bad"}
    )

    assert result["message"] == "A valid email is required for registration."


def test_login_controller_register_success():
    controller = LoginController()
    controller.auth_service = FakeAuthService()

    result = controller.register_request(
        {
            "username": "alice",
            "password": "password123",
            "role": "patient",
            "email": "alice@example.com",
        }
    )

    assert result["status"] == "success"
    assert result["email"] == "alice@example.com"


def test_login_controller_login_validation_and_success():
    controller = LoginController()
    controller.auth_service = FakeAuthService()

    assert controller.login_request({})["message"] == "Username is required."
    assert controller.login_request({"username": "a"})[
        "message"] == "Password is required."

    missing_role = controller.login_request({"username": "a", "password": "p"})
    assert missing_role["message"] == "Role is required."

    result = controller.login_request(
        {"username": "alice", "password": "password123", "role": "patient"}
    )

    assert result["status"] == "pending"


def test_login_controller_verify_mfa_and_logout():
    controller = LoginController()
    controller.auth_service = FakeAuthService()

    assert controller.verify_mfa_request(
        {})["message"] == "Username is required."
    assert controller.verify_mfa_request({"username": "alice"})[
        "message"] == "MFA code is required."

    verify_result = controller.verify_mfa_request(
        {"username": "alice", "code": "654321"})
    assert verify_result["status"] == "success"

    assert controller.logout_request({})["message"] == "Username is required."

    logout_result = controller.logout_request({"username": "alice"})
    assert logout_result["status"] == "success"


def test_admin_controller_user_not_found():
    controller = AdminController()
    controller.user_repository = FakeUserRepository(user=None)

    result = controller.get_audit_logs("missing")

    assert result["status"] == "failure"
    assert result["message"] == "User not found"


def test_admin_controller_access_denied():
    user = SimpleNamespace(username="bob", role="patient")
    controller = AdminController()
    controller.user_repository = FakeUserRepository(user=user)
    controller.access_control_service = FakeAccessControlService(
        authorized=False)
    controller.audit_logger = FakeAuditLogger()

    result = controller.get_audit_logs("bob")

    assert result["status"] == "failure"
    assert result["message"] == "Access denied"
    assert controller.audit_logger.logged[0][0] == "audit_access_denied"


def test_admin_controller_success():
    user = SimpleNamespace(username="alice", role="admin")
    controller = AdminController()
    controller.user_repository = FakeUserRepository(user=user)
    controller.access_control_service = FakeAccessControlService(
        authorized=True)
    controller.audit_logger = FakeAuditLogger()

    result = controller.get_audit_logs("alice")

    assert result["status"] == "success"
    assert result["logs"][0]["event_type"] == "login_success"


def test_record_controller_user_not_found():
    controller = RecordController()
    controller.user_repository = FakeUserRepository(user=None)

    result = controller.get_record(1, "missing")

    assert result["status"] == "failure"
    assert result["message"] == "User not found"


def test_record_controller_success():
    user = SimpleNamespace(username="alice", role="admin")
    controller = RecordController()
    controller.user_repository = FakeUserRepository(user=user)
    controller.record_service = FakeRecordService()

    result = controller.get_record(1, "alice")

    assert result["status"] == "success"
    assert result["record"]["record_id"] == 1


def test_flask_home_route():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Secure Access Portal backend is running" in response.data


def test_auth_routes_register_login_verify_logout(monkeypatch):
    app = create_app()
    client = app.test_client()

    from apps.routes import authRoutes

    authRoutes.login_controller.auth_service = FakeAuthService()

    register_response = client.post(
        "/register",
        json={
            "username": "alice",
            "password": "password123",
            "role": "patient",
            "email": "alice@example.com",
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/login",
        json={
            "username": "alice",
            "password": "password123",
            "role": "patient",
        },
    )
    assert login_response.status_code == 200

    verify_response = client.post(
        "/verify-mfa",
        json={"username": "alice", "code": "654321"},
    )
    assert verify_response.status_code == 200

    logout_response = client.post("/logout", json={"username": "alice"})
    assert logout_response.status_code == 200


def test_auth_routes_validation_errors():
    app = create_app()
    client = app.test_client()

    assert client.post("/register", json={}).status_code == 400
    assert client.post("/login", json={}).status_code == 400
    assert client.post("/verify-mfa", json={}).status_code == 400
    assert client.post("/logout", json={}).status_code == 400


def test_admin_routes(monkeypatch):
    app = create_app()
    client = app.test_client()

    from apps.routes import adminroutes

    class FakeAdminController:
        def get_audit_logs(self, username):
            return {"status": "success", "logs": []}

    adminroutes.admin_controller = FakeAdminController()

    health_response = client.get("/admin/health")
    assert health_response.status_code == 200

    missing_username = client.get("/admin/audit")
    assert missing_username.status_code == 400

    audit_response = client.get("/admin/audit?username=alice")
    assert audit_response.status_code == 200
    assert audit_response.get_json()["status"] == "success"


def test_record_routes(monkeypatch):
    app = create_app()
    client = app.test_client()

    from apps.routes import recordroutes

    class FakeRecordController:
        def get_record(self, record_id, username):
            return {
                "status": "success",
                "record_id": record_id,
                "username": username}

    recordroutes.record_controller = FakeRecordController()

    missing_username = client.get("/records/1")
    assert missing_username.status_code == 400

    record_response = client.get("/records/1?username=alice")
    assert record_response.status_code == 200
    assert record_response.get_json()["record_id"] == 1


def test_role_model_permission_checks():
    role = Role(
        role_name="admin",
        permissions=[
            "review_logs",
            "view_masked_record"])

    assert role.role_name == "admin"
    assert role.has_permission("review_logs") is True
    assert role.has_permission("delete_records") is False


def test_session_model_valid_and_expired():
    current_session = Session.create_new(
        "session-1", "alice", duration_minutes=30)
    assert current_session.session_id == "session-1"
    assert current_session.username == "alice"
    assert current_session.is_valid() is True

    expired_session = Session(
        session_id="session-2",
        username="alice",
        created_at=datetime.now(timezone.utc) - timedelta(minutes=60),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    assert expired_session.is_valid() is False


def test_mfa_abstract_methods_are_covered():
    strategy = DummyMFAStrategy()

    assert strategy.send_code(SimpleNamespace(username="alice")) is None
    assert strategy.verify_code(
        SimpleNamespace(
            username="alice"),
        "123456") is None


def test_email_otp_strategy_no_email(capsys):
    strategy = EmailOTPStrategy()
    user = SimpleNamespace(username="alice", email="")

    strategy.send_code(user)

    captured = capsys.readouterr()
    assert "No email provided" in captured.out


def test_email_otp_strategy_missing_environment(capsys):
    strategy = EmailOTPStrategy()
    user = SimpleNamespace(username="alice", email="alice@example.com")

    strategy.send_code(user)

    captured = capsys.readouterr()
    assert "Missing environment variable" in captured.out


def test_email_otp_strategy_success(monkeypatch, capsys):
    sent_messages = []

    class FakeSendGridClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def send(self, message):
            sent_messages.append(message)

    monkeypatch.setenv("FROM_EMAIL", "sender@example.com")
    monkeypatch.setenv("SENDGRID_API_KEY", "fake-key")
    monkeypatch.setattr(
        "apps.security.mfaStrategies.SendGridAPIClient",
        FakeSendGridClient,
    )
    monkeypatch.setattr(
        "apps.security.mfaStrategies.random.randint",
        lambda a,
        b: 123456)

    strategy = EmailOTPStrategy()
    user = SimpleNamespace(username="alice", email="alice@example.com")

    strategy.send_code(user)

    captured = capsys.readouterr()
    assert "Code sent" in captured.out
    assert sent_messages
    assert strategy.verify_code(user, "123456") is True
    assert strategy.verify_code(user, "123456") is False


def test_email_otp_strategy_sendgrid_exception(monkeypatch, capsys):
    class BrokenSendGridClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def send(self, message):
            raise RuntimeError("send failed")

    monkeypatch.setenv("FROM_EMAIL", "sender@example.com")
    monkeypatch.setenv("SENDGRID_API_KEY", "fake-key")
    monkeypatch.setattr(
        "apps.security.mfaStrategies.SendGridAPIClient",
        BrokenSendGridClient,
    )

    strategy = EmailOTPStrategy()
    user = SimpleNamespace(username="alice", email="alice@example.com")

    strategy.send_code(user)

    captured = capsys.readouterr()
    assert "Failed to send email" in captured.out


def test_totp_strategy_send_and_verify(capsys):
    strategy = TOTPStrategy()
    user = SimpleNamespace(username="alice")

    strategy.send_code(user)
    captured = capsys.readouterr()

    assert "TOTP ready for user alice" in captured.out
    assert strategy.verify_code(user, "654321") is True
    assert strategy.verify_code(user, "000000") is False
