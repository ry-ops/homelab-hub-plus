"""
Bearer token auth middleware.

Protects all /api/* routes except the public whitelist.
Dev mode: if API_TOKEN env var is not set, all requests pass through.
"""
import os

from flask import current_app, jsonify, request

# Routes that never require a token
PUBLIC_PATHS = {"/api/health", "/api/config"}


def register_auth_middleware(app):
    @app.before_request
    def check_auth():
        # Only guard /api/* paths
        if not request.path.startswith("/api/"):
            return

        # Allow public endpoints unconditionally
        if request.path in PUBLIC_PATHS:
            return

        api_token = current_app.config.get("API_TOKEN") or ""

        # Dev mode: no token configured → open access
        if not api_token:
            return

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(error="Unauthorized"), 401

        provided = auth_header[len("Bearer "):]
        if provided != api_token:
            return jsonify(error="Forbidden"), 403
