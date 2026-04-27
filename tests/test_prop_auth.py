"""Property-based tests for authentication input handling."""

import os

from hypothesis import given
from hypothesis import strategies as st

from apps.services.authSvc import AuthService


@given(
    username=st.text(min_size=1, max_size=20),
    password=st.text(min_size=1, max_size=20),
    role=st.sampled_from(["patient", "admin", "auditor"]),
)
def test_authenticate_returns_known_status(
    username: str,
    password: str,
    role: str,
):
    """
    Property-based test.

    Hypothesis generates many username, password, and role combinations.
    The authenticate method should always return a recognized status instead
    of crashing on unexpected input.
    """
    os.environ["MFA_METHOD"] = "totp"

    service = AuthService()

    result = service.authenticate(
        username=username,
        password=password,
        role=role,
    )

    assert result["status"] in {"error", "pending", "success"}
