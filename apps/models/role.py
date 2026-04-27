from dataclasses import dataclass, field
from typing import List


@dataclass
class Role:
    """
    Role model.

    A role groups permissions together. This is the core idea behind
    role-based access control, where users are assigned roles and roles
    determine what actions are allowed.
    """
    role_name: str
    permissions: List[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        """
        Return True if this role includes the requested permission.
        """
        return permission in self.permissions
