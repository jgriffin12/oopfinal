from flask import Flask
from flask_cors import CORS

from apps.routes.authRoutes import auth_bp
from apps.routes.recordroutes import record_bp
from apps.routes.adminroutes import admin_bp


def create_app() -> Flask:
    """
    Creates and configures the Flask application.

    This function follows the application factory pattern.
    It keeps app setup in one place and makes the Flask app easier
    to test, extend, and maintain.
    """

    # Create the main Flask application object.
    app = Flask(__name__)

    # Enable Cross-Origin Resource Sharing.
    # This allows the frontend to send requests to the Flask backend,
    # especially when the frontend and backend run on different URLs or ports.
    CORS(app)

    # Secret key used by Flask for session security and internal signing.
    # This is acceptable for development, but in production this should
    # be stored in an environment variable.
    app.config["SECRET_KEY"] = "dev-secret-key"

    # Register the authentication routes.
    # These routes handle login and MFA verification.
    app.register_blueprint(auth_bp)

    # Register the protected medical record routes.
    # These routes handle access to patient record data.
    app.register_blueprint(record_bp)

    # Register the admin routes.
    # These routes support administrative/backend health checks.
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home() -> str:
        """
        Basic health check route.

        This confirms that the Flask backend is running.
        """
        return "Secure Access Portal backend is running."

    return app


# Create the Flask app instance.
# This allows Flask, Gunicorn, or other WSGI servers to import the app.
app = create_app()


if __name__ == "__main__":  # pragma: no cover
    # Run the app locally for development and class demo purposes.
    # host="0.0.0.0" allows Codespaces or Docker to expose the app externally.
    # debug=True gives helpful error messages during development.
    app.run(host="0.0.0.0", port=5000, debug=True)  # pragma: no cover
