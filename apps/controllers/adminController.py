from apps.repositories.userRepo import UserRepository
from apps.services.accessControlSvc import AccessControlService
from apps.services.auditLogger import AuditLogger


class AdminController:
    """
    Controller for admin-only features such as viewing audit logs.
    """

    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.access_control_service = AccessControlService()
        self.audit_logger = AuditLogger()

    def get_audit_logs(self, username: str) -> dict:
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {"status": "failure", "message": "User not found"}

        if not self.access_control_service.is_authorized(user, "review_logs"):
            self.audit_logger.log_event(
                "audit_access_denied", username, "failure")
            return {"status": "failure", "message": "Access denied"}

        events = self.audit_logger.get_all_events()
        self.audit_logger.log_event("audit_logs_viewed", username, "success")

        return {
            "status": "success",
            "logs": [
                {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "username": event.username,
                    "status": event.status,
                }
                for event in events
            ],
        }
