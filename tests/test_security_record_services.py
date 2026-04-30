"""Tests for security utilities, MFA factory, MFA service, and record service."""

import pytest

from apps.models.user import User
from apps.repositories.recordRepo import RecordRepository
from apps.security.masker import SensitiveDataMasker
from apps.security.mfaFactory import MFAFactory
from apps.security.mfaStrategies import TOTPStrategy
from apps.security.tokenizer import Tokenizer
from apps.services.accessControlSvc import AccessControlService
from apps.services.mfaSvc import MFAService
from apps.services.recordSvc import RecordService


def make_user(role: str = "provider") -> User:
    """Create a user object for service tests."""
    return User(
        user_id=1,
        username="alice",
        password_hash="hashed",
        email="alice@example.com",
        role=role,
    )


def test_mask_ssn_normal_value():
    """SSNs should show only the last four digits."""
    masker = SensitiveDataMasker()

    assert masker.mask_ssn("123-45-6789") == "***-**-6789"


def test_mask_ssn_short_value():
    """Short SSN-like values should be fully masked."""
    masker = SensitiveDataMasker()

    assert masker.mask_ssn("123") == "****"


def test_mask_name_normal_value():
    """Names should keep the first letter and mask the rest."""
    masker = SensitiveDataMasker()

    assert masker.mask_name("Alice") == "A****"


def test_mask_name_empty_value():
    """Empty names should return an empty string."""
    masker = SensitiveDataMasker()

    assert masker.mask_name("") == ""


def test_tokenizer_returns_expected_prefix_and_length():
    """Tokenizer should return a stable token format."""
    tokenizer = Tokenizer()

    token = tokenizer.tokenize("123-45-6789")

    assert token.startswith("TOKEN-")
    assert len(token) == len("TOKEN-") + 12
    assert token == tokenizer.tokenize("123-45-6789")


def test_record_repository_finds_existing_record():
    """RecordRepository should return records that exist."""
    repository = RecordRepository()

    record = repository.find_by_id(1)

    assert record is not None
    assert record.record_id == 1
    assert record.patient_name == "Jane Doe"


def test_record_repository_returns_none_for_missing_record():
    """RecordRepository should return None for missing records."""
    repository = RecordRepository()

    assert repository.find_by_id(999) is None


def test_access_control_allows_provider_record_access():
    """Provider users should be authorized for masked record viewing."""
    service = AccessControlService()
    user = make_user(role="provider")

    assert service.is_authorized(user, "view_masked_record") is True


def test_access_control_allows_admin_audit_logs_only():
    """Admin users should be authorized for audit logs, not patient records."""
    service = AccessControlService()
    user = make_user(role="admin")

    assert service.is_authorized(user, "review_logs") is True
    assert service.is_authorized(user, "view_masked_record") is False


def test_access_control_allows_patient_own_record_only():
    """Patient users should only have patient-level access."""
    service = AccessControlService()
    user = make_user(role="patient")

    assert service.is_authorized(user, "view_own_record") is True
    assert service.is_authorized(user, "view_masked_record") is False
    assert service.is_authorized(user, "review_logs") is False


def test_access_control_denies_unknown_role():
    """Unknown roles should not be authorized."""
    service = AccessControlService()
    user = make_user(role="guest")

    assert service.is_authorized(user, "view_masked_record") is False


def test_record_service_returns_masked_record_for_authorized_provider():
    """Authorized providers should receive masked and tokenized record data."""
    service = RecordService()
    user = make_user(role="provider")

    result = service.get_masked_record(user, 1)

    assert result["status"] == "success"
    assert result["record"]["patient_name"] == "J*******"
    assert result["record"]["ssn_masked"] == "***-**-6789"
    assert result["record"]["ssn_token"].startswith("TOKEN-")
    assert "asthma" in result["record"]["medical_notes"].lower()


def test_record_service_denies_admin_record_access():
    """Admin users should not receive protected patient records."""
    service = RecordService()
    user = make_user(role="admin")

    result = service.get_masked_record(user, 1)

    assert result["status"] == "failure"
    assert result["message"] == "Access denied"


def test_record_service_denies_patient_record_access():
    """Patient users should not receive protected provider records."""
    service = RecordService()
    user = make_user(role="patient")

    result = service.get_masked_record(user, 1)

    assert result["status"] == "failure"
    assert result["message"] == "Access denied"


def test_record_service_denies_unauthorized_user():
    """Unauthorized users should not receive protected records."""
    service = RecordService()
    user = make_user(role="guest")

    result = service.get_masked_record(user, 1)

    assert result["status"] == "failure"
    assert result["message"] == "Access denied"


def test_record_service_handles_missing_record():
    """Authorized providers should receive a not-found message for missing records."""
    service = RecordService()
    user = make_user(role="provider")

    result = service.get_masked_record(user, 999)

    assert result["status"] == "failure"
    assert result["message"] == "Record not found"


def test_mfa_factory_creates_totp_strategy():
    """The MFA factory should create the TOTP strategy."""
    factory = MFAFactory()

    strategy = factory.create_strategy("totp")

    assert isinstance(strategy, TOTPStrategy)


def test_mfa_factory_rejects_unknown_strategy():
    """The MFA factory should reject unsupported strategy names."""
    factory = MFAFactory()

    with pytest.raises(ValueError):
        factory.create_strategy("sms")


def test_mfa_service_verifies_totp_code_success():
    """MFAService should verify the backup TOTP code."""
    service = MFAService()
    user = make_user()

    assert service.verify_mfa_code(user, "654321", "totp") is True


def test_mfa_service_verifies_totp_code_failure():
    """MFAService should reject an incorrect backup TOTP code."""
    service = MFAService()
    user = make_user()

    assert service.verify_mfa_code(user, "000000", "totp") is False


def test_mfa_service_sends_totp_code(capsys):
    """Sending a TOTP code should print the demo MFA code."""
    service = MFAService()
    user = make_user()

    service.send_mfa_code(user, "totp")

    captured = capsys.readouterr()
    assert "TOTP ready for user alice" in captured.out
