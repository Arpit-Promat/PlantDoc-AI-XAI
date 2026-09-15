"""Account verification, OTP-based 2FA, and product-page routes for ATHARVADRISHTI."""

from __future__ import annotations

import os
import re
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from functools import wraps

import jwt
from flask import current_app, jsonify, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

from database import db, User
from security import limiter, get_current_user

OTP_TTL_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
OTP_LENGTH = 6
PHONE_RE = re.compile(r"^\+?[1-9]\d{9,14}$")


class UserSecurity(db.Model):
    __tablename__ = "user_security"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    mobile_verified = db.Column(db.Boolean, nullable=False, default=False)
    two_factor_enabled = db.Column(db.Boolean, nullable=False, default=False)
    two_factor_channel = db.Column(db.String(20), nullable=False, default="email")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AuthChallenge(db.Model):
    __tablename__ = "auth_challenges"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    purpose = db.Column(db.String(30), nullable=False, index=True)
    channel = db.Column(db.String(20), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)


def normalize_phone(phone: str) -> str:
    value = str(phone or "").strip().replace(" ", "")
    if value.startswith("00"):
        value = "+" + value[2:]
    return value


def valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.fullmatch(phone or ""))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _security_for(user: User) -> UserSecurity:
    state = UserSecurity.query.filter_by(user_id=user.id).first()
    if state is None:
        state = UserSecurity(user_id=user.id)
        db.session.add(state)
        db.session.flush()
    return state


def _make_otp() -> str:
    return f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"


def _issue_challenge(user: User, purpose: str, channel: str, destination: str) -> AuthChallenge:
    AuthChallenge.query.filter_by(user_id=user.id, purpose=purpose, used_at=None).update({"used_at": _now()})
    code = _make_otp()
    challenge = AuthChallenge(
        user_id=user.id,
        purpose=purpose,
        channel=channel,
        destination=destination,
        code_hash=generate_password_hash(code),
        expires_at=_now() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    db.session.add(challenge)
    db.session.commit()
    _deliver_code(destination, channel, code, purpose)
    return challenge


def _deliver_code(destination: str, channel: str, code: str, purpose: str) -> None:
    subject = {
        "email_verification": "Verify your ATHARVADRISHTI email",
        "mobile_verification": "Verify your ATHARVADRISHTI mobile number",
        "login_2fa": "Your ATHARVADRISHTI security code",
    }.get(purpose, "Your ATHARVADRISHTI verification code")
    if channel == "email":
        _send_email(destination, subject, f"Your ATHARVADRISHTI verification code is {code}. It expires in {OTP_TTL_MINUTES} minutes.")
    else:
        _send_sms(destination, f"ATHARVADRISHTI code: {code}. Expires in {OTP_TTL_MINUTES} minutes.")


def _send_email(destination: str, subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST", "").strip()
    if not host:
        current_app.logger.warning("EMAIL DEV FALLBACK destination=%s body=%s", destination, body)
        return
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("EMAIL_FROM", username or "no-reply@atharvadrishti.local")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = destination
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        if os.getenv("SMTP_USE_TLS", "1") == "1":
            smtp.starttls()
        if username:
            smtp.login(username, password)
        smtp.send_message(message)


def _send_sms(destination: str, body: str) -> None:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    if not (account_sid and auth_token and from_number):
        current_app.logger.warning("SMS DEV FALLBACK destination=%s body=%s", destination, body)
        return
    try:
        from twilio.rest import Client
        Client(account_sid, auth_token).messages.create(body=body, from_=from_number, to=destination)
    except ImportError as exc:
        raise RuntimeError("Twilio SDK is not installed; configure the SMS provider dependency.") from exc


def _verify_challenge(user: User, purpose: str, code: str, channel: str | None = None) -> bool:
    query = AuthChallenge.query.filter_by(user_id=user.id, purpose=purpose, used_at=None)
    if channel:
        query = query.filter_by(channel=channel)
    challenge = query.order_by(AuthChallenge.created_at.desc()).first()
    if challenge is None or challenge.expires_at < _now() or challenge.attempts >= MAX_OTP_ATTEMPTS:
        return False
    challenge.attempts += 1
    if not check_password_hash(challenge.code_hash, str(code or "")):
        db.session.commit()
        return False
    challenge.used_at = _now()
    db.session.commit()
    return True


def _issue_access_token(user: User) -> str:
    now = _now()
    payload = {"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=12), "iss": "atharvadrishti"}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _auth_json_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        request.current_user = user
        return view(*args, **kwargs)
    return wrapped


def register_auth_feature_routes(app):
    @app.get("/landing")
    def landing_page():
        return render_template("landing.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/signup")
    def signup_page():
        return render_template("signup.html")

    @app.get("/verify")
    def verify_page():
        return render_template("verify.html")

    @app.get("/two-factor")
    def two_factor_page():
        return render_template("two_factor.html")

    @app.post("/api/auth/register")
    @limiter.limit("5 per minute")
    def register_account():
        from werkzeug.security import generate_password_hash
        data = request.get_json(silent=True) or {}
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        phone = normalize_phone(data.get("phone", ""))
        password = str(data.get("password", ""))
        if not name or len(name) > 120:
            return jsonify({"error": "Name is required"}), 400
        if not email or "@" not in email or len(email) > 255:
            return jsonify({"error": "Valid email is required"}), 400
        if not valid_phone(phone):
            return jsonify({"error": "Valid mobile number with country code is required"}), 400
        if len(password) < 8 or len(password) > 128:
            return jsonify({"error": "Password must be 8 to 128 characters"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Unable to create account"}), 409

        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.flush()
        user.phone_number = phone
        state = UserSecurity(user_id=user.id)
        db.session.add(state)
        db.session.commit()

        try:
            _issue_challenge(user, "email_verification", "email", email)
            _issue_challenge(user, "mobile_verification", "sms", phone)
        except Exception:
            app.logger.exception("Verification delivery failed during registration")

        return jsonify({"id": user.id, "name": user.name, "email": user.email, "phone": phone, "verification_required": True}), 201

    @app.post("/api/auth/verify-email")
    @limiter.limit("10 per minute")
    def verify_email():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        code = str(data.get("code", "")).strip()
        user = User.query.filter_by(email=email).first()
        if user is None or not _verify_challenge(user, "email_verification", code, "email"):
            return jsonify({"error": "Invalid or expired verification code"}), 400
        _security_for(user).email_verified = True
        db.session.commit()
        return jsonify({"verified": True, "email_verified": True})

    @app.post("/api/auth/verify-mobile")
    @limiter.limit("10 per minute")
    def verify_mobile():
        data = request.get_json(silent=True) or {}
        phone = normalize_phone(data.get("phone", ""))
        code = str(data.get("code", "")).strip()
        user = User.query.filter_by(phone_number=phone).first()
        if user is None or not _verify_challenge(user, "mobile_verification", code, "sms"):
            return jsonify({"error": "Invalid or expired verification code"}), 400
        _security_for(user).mobile_verified = True
        db.session.commit()
        return jsonify({"verified": True, "mobile_verified": True})

    @app.post("/api/auth/resend-verification")
    @limiter.limit("3 per 10 minutes")
    def resend_verification():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"message": "If the account exists, a verification code has been sent."})
        state = _security_for(user)
        try:
            if not state.email_verified:
                _issue_challenge(user, "email_verification", "email", user.email)
            if getattr(user, "phone_number", None) and not state.mobile_verified:
                _issue_challenge(user, "mobile_verification", "sms", user.phone_number)
        except Exception:
            app.logger.exception("Verification resend failed")
        return jsonify({"message": "Verification codes processed."})

    @app.post("/api/auth/login")
    @limiter.limit("5 per minute")
    def login_with_security():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))
        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password"}), 401

        state = _security_for(user)
        if not state.email_verified or not state.mobile_verified:
            return jsonify({
                "error": "Account verification required",
                "verification_required": True,
                "email_verified": state.email_verified,
                "mobile_verified": state.mobile_verified,
            }), 403
        if state.two_factor_enabled:
            channel = state.two_factor_channel if state.two_factor_channel in {"email", "sms"} else "email"
            destination = user.email if channel == "email" else getattr(user, "phone_number", None)
            if not destination:
                return jsonify({"error": "2FA channel is not available"}), 400
            _issue_challenge(user, "login_2fa", channel, destination)
            return jsonify({"two_factor_required": True, "channel": channel, "expires_in": OTP_TTL_MINUTES * 60})
        return jsonify({"access_token": _issue_access_token(user), "token_type": "Bearer", "expires_in": 43200})

    @app.post("/api/auth/2fa/verify")
    @limiter.limit("10 per minute")
    def verify_login_2fa():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        code = str(data.get("code", "")).strip()
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"error": "Invalid verification code"}), 401
        state = _security_for(user)
        channel = state.two_factor_channel if state.two_factor_enabled else None
        if not state.two_factor_enabled or not _verify_challenge(user, "login_2fa", code, channel):
            return jsonify({"error": "Invalid or expired two-factor code"}), 401
        return jsonify({"access_token": _issue_access_token(user), "token_type": "Bearer", "expires_in": 43200})

    @app.post("/api/auth/2fa/setup")
    @_auth_json_required
    def setup_2fa():
        state = _security_for(request.current_user)
        if not state.email_verified or not state.mobile_verified:
            return jsonify({"error": "Verify both email and mobile before enabling 2FA"}), 400
        channel = str((request.get_json(silent=True) or {}).get("channel", state.two_factor_channel)).lower()
        if channel not in {"email", "sms"}:
            return jsonify({"error": "Channel must be email or sms"}), 400
        state.two_factor_channel = channel
        db.session.commit()
        destination = request.current_user.email if channel == "email" else getattr(request.current_user, "phone_number", None)
        _issue_challenge(request.current_user, "login_2fa", channel, destination)
        return jsonify({"message": "2FA verification code sent", "channel": channel})

    @app.post("/api/auth/2fa/enable")
    @_auth_json_required
    def enable_2fa():
        state = _security_for(request.current_user)
        data = request.get_json(silent=True) or {}
        code = str(data.get("code", "")).strip()
        channel = state.two_factor_channel
        if not _verify_challenge(request.current_user, "login_2fa", code, channel):
            return jsonify({"error": "Invalid or expired 2FA setup code"}), 400
        state.two_factor_enabled = True
        db.session.commit()
        return jsonify({"two_factor_enabled": True, "channel": channel})

    @app.post("/api/auth/2fa/disable")
    @_auth_json_required
    def disable_2fa():
        state = _security_for(request.current_user)
        state.two_factor_enabled = False
        db.session.commit()
        return jsonify({"two_factor_enabled": False})

    @app.get("/api/auth/security-status")
    @_auth_json_required
    def security_status():
        state = _security_for(request.current_user)
        return jsonify({
            "email_verified": state.email_verified,
            "mobile_verified": state.mobile_verified,
            "two_factor_enabled": state.two_factor_enabled,
            "two_factor_channel": state.two_factor_channel,
        })
