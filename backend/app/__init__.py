import os

from flask import Flask, jsonify, send_from_directory

from .config import Config
from .services.cache import init_cache
from .services.gitstore import init_gitstore


def create_app(config_class=Config):
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    app = Flask(__name__, static_folder=static_dir, static_url_path="")

    app.config.from_object(config_class)

    init_cache(app)
    init_gitstore(app)

    # Enable CORS for development
    try:
        from flask_cors import CORS
        CORS(app)
    except ImportError:
        pass

    # Auth middleware — must be registered before blueprints
    from .middleware.auth import register_auth_middleware
    register_auth_middleware(app)

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify(status="ok")

    # Config — returns whether auth is required and the app version
    @app.route("/api/config")
    def api_config():
        requires_auth = bool(app.config.get("API_TOKEN"))
        return jsonify(requiresAuth=requires_auth, version="1.1.0")

    # SPA catch-all: serve index.html for all non-API routes
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        api_prefixes = ("api/", "hardware/", "vms/", "apps/",
                       "storage/", "shares/", "networks/", "misc/", "documents/", "map/")
        if path.startswith(api_prefixes):
            return jsonify(error="Not found"), 404
        file_path = os.path.join(static_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(static_dir, path)
        return send_from_directory(static_dir, "index.html")

    return app
