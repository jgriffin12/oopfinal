from flask import Flask
from flask_cors import CORS

# Import each blueprint so the application can register its route groups.
from apps.routes.authRoutes import auth_bp
from apps.routes.recordroutes import record_bp
from apps.routes.adminroutes import admin_bp


def create_app() -> Flask:
    """
    Application factory.

    This function creates and configures the Flask app instance.
    Using a factory makes the app easier to test and easier to scale later.
    """
    app = Flask(__name__)

    CORS(app)

    # Secret key is used by Flask for sessions and other security-related features.
    # This hardcoded value is fine for early development, but later it should come
    # from an environment variable.
    app.config["SECRET_KEY"] = "dev-secret-key"

    # Register each blueprint so its routes become part of the application.
    app.register_blueprint(auth_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home(): 
        return "Secure Access Portal backend is running."
        
    return app


# Create the app object at module level so Flask can run it.
app = create_app()


if __name__ == "__main__":
    # Run the development server locally.
    # host="0.0.0.0" allows Docker/container access.
    # debug=True is convenient for development but should be disabled in production.
    app.run(host="0.0.0.0", port=5000, debug=True)