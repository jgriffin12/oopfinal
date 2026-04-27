from flask import Blueprint, jsonify, request
from apps.controllers.adminController import AdminController

# Blueprint for administrative routes such as user management or log review.
admin_bp = Blueprint("admin", __name__)

admin_controller = AdminController()


@admin_bp.route("/admin/health", methods=["GET"])
def admin_health():
    """
    Simple placeholder route to confirm that the admin blueprint is active.

    This is useful early in development to verify that blueprint
    registration works.
    """
    return jsonify({"status": "admin route ready"})


@admin_bp.route("/admin/audit", methods=["GET"])
def get_audit_logs():
    """
    Return audit logs for authorized admin users.
    """
    username = request.args.get("username")

    if not username:
        return jsonify(
            {"status": "failure", "message": "Username required"}), 400

    return jsonify(admin_controller.get_audit_logs(username))
