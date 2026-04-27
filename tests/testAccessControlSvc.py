from app.models.user import User
from app.services.access_control_service import AccessControlService


def test_doctor_can_view_masked_record():
    """
    Doctors should be allowed to view masked records.
    """
    service = AccessControlService()
    user = User(1, "alice", "hash", "alice@example.com", "doctor")

    assert service.is_authorized(user, "view_masked_record") is True


def test_nurse_cannot_manage_users():
    """
    Nurses should not be allowed to perform admin-only actions.
    """
    service = AccessControlService()
    user = User(2, "nina", "hash", "nina@example.com", "nurse")

    assert service.is_authorized(user, "manage_users") is False
