from flask import Blueprint, jsonify, request
from apps.controllers.recordController import RecordController

# Blueprint for all protected-record routes.
record_bp = Blueprint("records", __name__)

record_controller = RecordController()


@record_bp.route("/records/<int:record_id>", methods=["GET"])
def get_record(record_id: int):
    """
    Placeholder route for fetching a protected record.

    Later this route should:
    1. Check the current authenticated user
    2. Call the record controller
    3. Enforce RBAC
    4. Return masked/tokenized sensitive data
    """
    username = request.args.get("username")

    if not username:
        return jsonify(
            {"status": "failure", "message": "Username required."}), 400

    return jsonify(record_controller.get_record(record_id, username))
