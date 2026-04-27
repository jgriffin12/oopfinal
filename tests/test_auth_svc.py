"""Tests for the AuthService registration, login, and MFA flow."""

from apps.services.authSvc import AuthService


def test_authenticate_invalid_user(tmp_path, monkeypatch):
    """
    Unknown usernames should fail authentication.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    result = service.authenticate(
        username="unknown",
        password="password123",
        role="patient",
    )

    assert result["status"] == "error"
    assert "Invalid username or password" in result["message"]


def test_register_user_success(tmp_path, monkeypatch):
    """
    A new user should be able to register with an email.
    """
    monkeypatch.chdir(tmp_path)

    service = AuthService()

    result = service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    assert result["status"] == "success"
    assert result["username"] == "chica"
    assert result["role"] == "patient"


def test_register_duplicate_user_fails(tmp_path, monkeypatch):
    """
    Duplicate usernames should not be allowed.
    """
    monkeypatch.chdir(tmp_path)

    service = AuthService()

    service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    result = service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="other@example.com",
    )

    assert result["status"] == "error"
    assert "already exists" in result["message"]


def test_authenticate_valid_user_pending_mfa(tmp_path, monkeypatch):
    """
    Valid username, password, and role should move the user to the MFA step.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    result = service.authenticate(
        username="chica",
        password="password123",
        role="patient",
    )

    assert result["status"] == "pending"
    assert result["username"] == "chica"
    assert result["role"] == "patient"


def test_authenticate_wrong_password_fails(tmp_path, monkeypatch):
    """
    A wrong password should fail before MFA.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    result = service.authenticate(
        username="chica",
        password="wrongpassword",
        role="patient",
    )

    assert result["status"] == "error"
    assert "Invalid username or password" in result["message"]


def test_authenticate_wrong_role_fails(tmp_path, monkeypatch):
    """
    A valid user with the wrong selected role should fail.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    result = service.authenticate(
        username="chica",
        password="password123",
        role="admin",
    )

    assert result["status"] == "error"
    assert "Selected role does not match" in result["message"]


def test_verify_mfa_success(tmp_path, monkeypatch):
    """
    The backup TOTP code should complete MFA verification.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    result = service.verify_mfa(
        username="chica",
        code="654321",
    )

    assert result["status"] == "success"
    assert result["username"] == "chica"
    assert result["role"] == "patient"


def test_verify_mfa_wrong_code_fails(tmp_path, monkeypatch):
    """
    An incorrect MFA code should fail.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    result = service.verify_mfa(
        username="chica",
        code="000000",
    )

    assert result["status"] == "error"
    assert "Invalid MFA code" in result["message"]
