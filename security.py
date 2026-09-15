"""Security helpers for ATHARVADRISHTI.

This module adds backend security without requiring any frontend/template change.
"""

import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import User

ALGORITHM = "HS256"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MiB


def configure_security(app):
    """Configure security defaults and register backend authentication routes."""
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        secret_key = "dev-only-change-this-secret-key"
    app.config["SECRET_KEY"] = secret_key
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", MAX_IMAGE_SIZE))
    app.config["MAX_FORM_MEMORY_SIZE"] = int(os.getenv("MAX_FORM_MEMORY_SIZE", 500_000))
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("COOKIE_SECURE", "0") == "1"

    trusted_hosts = os.getenv("TRUSTED_HOSTS", "").strip()
    if trusted_hosts:
        app.config["TRUSTED_HOSTS"] = [h.strip() for h in trusted_hosts.split(",") if h.strip()]

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy-Report-Only",
            "default-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'self'; base-uri 'self'",
        )
        if os.getenv("FORCE_HTTPS", "0") == "1":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"error": "Uploaded request is too large"}), 413

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        if not email or "@" not in email or len(email) > 255:
            return jsonify({"error": "Valid email is required"}), 400
        if len(password) < 8 or len(password) > 128:
            return jsonify({"error": "Password must be 8 to 128 characters"}), 400
        if len(name) > 120:
            return jsonify({"error": "Name is too long"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Unable to create account"}), 409

        user = User(name=name or None, email=email, password_hash=generate_password_hash(password))
        from database import db
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "name": user.name, "email": user.email}), 201

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401

        now = datetime.now(timezone.utc)
        payload = {"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=12), "iss": "atharvadrishti"}
        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm=ALGORITHM)
        return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": 43200})

    @app.get("/api/auth/me")
    @auth_required
    def me():
        return jsonify({"id": request.current_user.id, "name": request.current_user.name, "email": request.current_user.email})

    @app.before_request
    def protect_private_api():
        if request.path.startswith("/api/scans"):
            user = get_current_user()
            if user is None:
                return jsonify({"error": "Authentication required"}), 401
            request.current_user = user
        return None


def get_current_user():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[7:].strip()
    if not token:
        return None
    try:
        claims = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=[ALGORITHM],
            issuer="atharvadrishti",
            options={"require": ["sub", "iat", "exp", "iss"]},
        )
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None
    from database import db
    return db.session.get(User, user_id)


def auth_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        request.current_user = user
        return view(*args, **kwargs)
    return wrapped


def validate_uploaded_image(file_storage):
    """Validate filename, MIME type, extension and image signature/content."""
    if file_storage is None or not file_storage.filename:
        return False, "Please select an image."
    safe_name = secure_filename(file_storage.filename)
    if not safe_name:
        return False, "Invalid image filename."
    extension = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return False, "Unsupported image format."
    if file_storage.mimetype not in ALLOWED_IMAGE_MIME_TYPES:
        return False, "Unsupported image type."
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size <= 0 or size > MAX_IMAGE_SIZE:
        return False, "Image must be between 1 byte and 10 MB."
    try:
        from PIL import Image
        with Image.open(file_storage.stream) as img:
            img.verify()
        file_storage.stream.seek(0)
    except Exception:
        file_storage.stream.seek(0)
        return False, "The uploaded file is not a valid image."
    return True, safe_name
