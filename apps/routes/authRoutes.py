"""Authentication route definitions."""

from flask import Blueprint, jsonify, request

from apps.controllers.loginController import LoginController


# Blueprint groups together all authentication-related routes.
auth_bp = Blueprint("auth", __name__)

# Create one controller instance to handle auth request logic.
login_controller = LoginController()


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registration endpoint.

    The user provides their email one time during registration.
    Later login uses the stored email for MFA.
    """
    data = request.get_json() or {}
    result = login_controller.register_request(data)

    status_code = 400 if result.get("status") == "error" else 200
    return jsonify(result), status_code


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint.

    Login only requires username, password, and role.
    The stored email is used for MFA delivery.
    """
    data = request.get_json() or {}
    result = login_controller.login_request(data)

    status_code = 400 if result.get("status") == "error" else 200
    return jsonify(result), status_code


@auth_bp.route("/verify-mfa", methods=["POST"])
def verify_mfa():
    """MFA verification endpoint."""
    data = request.get_json() or {}
    result = login_controller.verify_mfa_request(data)

    status_code = 400 if result.get("status") == "error" else 200
    return jsonify(result), status_code


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout endpoint.

    For now this is a placeholder. Later it can invalidate a session or token.
    """
    data = request.get_json() or {}
    result = login_controller.logout_request(data)

    status_code = 400 if result.get("status") == "error" else 200
    return jsonify(result), status_code
