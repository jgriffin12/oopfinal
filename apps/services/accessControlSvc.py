class AccessControlService:
    """
    Service responsible for enforcing role-based access control.

    This service checks whether a user is allowed to perform a given action.
    In the starter version, permissions are mapped directly from role names.
    """

    def __init__(self) -> None:
        # Simple in-memory permission model for the prototype.
        self.role_permissions = {
            "doctor": {
                "view_record",
                "view_masked_record"},
            "nurse": {"view_masked_record"},
            "admin": {
                "view_record",
                "view_masked_record",
                "manage_users",
                "review_logs"},
            "auditor": {"review_logs"},
        }

    def is_authorized(self, user, action: str) -> bool:
        """
        Return True if the user's role is allowed to perform the action.
        """
        allowed_actions = self.role_permissions.get(user.role, set())
        return action in allowed_actions
