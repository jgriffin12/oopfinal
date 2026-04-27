from dataclasses import dataclass


@dataclass
class Permission:
    """
    Permission model.

    This starter version keeps permissions simple by storing only the
    permission name. Later, you could expand this to include descriptions
    or resource categories.
    """
    permission_name: str
