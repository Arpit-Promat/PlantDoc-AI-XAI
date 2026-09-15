"""Product authentication: email verification, mobile verification and OTP 2FA."""
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
from werkzeug.security import check_password_hash, generate_password_hash

from database import db, User
from security import get_current_user, limiter

PHONE_RE = re.compile(r"^\+?[1-9]\d{9,14}$")
OTP_TTL_MINUTES = 10
MAX_ATTEMPTS = 5


class AccountSecurity(db.Model):
    __tablename__ = "account_security"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=True, index=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    mobile_verified = db.Column(db.Boolean, nullable=False, default=False)
    two_factor_enabled = db.Column(db.Boolean, nullable=False, default=False)
    two_factor_channel = db.Column(db.String(10), nullable=False, default="email")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class VerificationCode(db.Model):
    __tablename__ = "verification_codes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    purpose = db.Column(db.String(32), nullable=False, index=True)
    channel = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)


def _now():
    return datetime.now(timezone.utc)


def normalize_phone(value):
    value = str(value or "").strip().replace(" ", "")
    return "+" + value[2:] if value.startswith("00") else value


def valid_phone(value):
    return bool(PHONE_RE.fullmatch(value or ""))


def _state(user):
    state = AccountSecurity.query.filter_by(user_id=user.id).first()
    if state is None:
        state = AccountSecurity(user_id=user.id)
        db.session.add(state)
        db.session.flush()
    return state


def _send_email(to_address, purpose, code):
    if not os.getenv("SMTP_HOST"):
        current_app.logger.warning("EMAIL DEV FALLBACK destination=%s code=%s", to_address, code)
        return
    subject = "Verify your ATHARVADRISHTI account" if purpose == "email_verification" else "Your ATHARVADRISHTI security code"
    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_FROM", os.getenv("SMTP_USERNAME", "no-reply@atharvadrishti.local"))
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(f"Your verification code is {code}. It expires in {OTP_TTL_MINUTES} minutes.")
    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587")), timeout=15) as smtp:
        if os.getenv("SMTP_USE_TLS", "1") == "1":
            smtp.starttls()
        username = os.getenv("SMTP_USERNAME", "")
        if username:
            smtp.login(username, os.getenv("SMTP_PASSWORD", ""))
        smtp.send_message(message)


def _send_sms(to_number, code):
    sid, token, from_number = os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"), os.getenv("TWILIO_FROM_NUMBER")
    if not (sid and token and from_number):
        current_app.logger.warning("SMS DEV FALLBACK destination=%s code=%s", to_number, code)
        return
    from twilio.rest import Client
    Client(sid, token).messages.create(body=f"ATHARVADRISHTI code: {code}", from_=from_number, to=to_number)


def issue_code(user, purpose, channel, destination):
    VerificationCode.query.filter_by(user_id=user.id, purpose=purpose, used_at=None).update({"used_at": _now()})
    code = f"{secrets.randbelow(1000000):06d}"
    row = VerificationCode(user_id=user.id, purpose=purpose, channel=channel, destination=destination, code_hash=generate_password_hash(code), expires_at=_now() + timedelta(minutes=OTP_TTL_MINUTES))
    db.session.add(row)
    db.session.commit()
    if channel == "email":
        _send_email(destination, purpose, code)
    else:
        _send_sms(destination, code)


def verify_code(user, purpose, channel, code):
    row = (VerificationCode.query.filter_by(user_id=user.id, purpose=purpose, channel=channel, used_at=None).order_by(VerificationCode.created_at.desc()).first())
    if not row or row.expires_at < _now() or row.attempts >= MAX_ATTEMPTS:
        return False
    row.attempts += 1
    ok = check_password_hash(row.code_hash, str(code or ""))
    if ok:
        row.used_at = _now()
    db.session.commit()
    return ok


def _token(user):
    stamp = _now()
    payload = {"sub": str(user.id), "iat": stamp, "exp": stamp + timedelta(hours=12), "iss": "atharvadrishti"}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _protected(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        request.current_user = user
        return view(*args, **kwargs)
    return wrapped


def register_product_auth_features(app):
    app.jinja_env.globals["auth_product_version"] = "1.0"

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

    @app.post("/api/product-auth/register")
    @limiter.limit("5 per minute")
    def register_product_account():
        data = request.get_json(silent=True) or {}
        name, email = str(data.get("name", "")).strip(), str(data.get("email", "")).strip().lower()
        phone, password = normalize_phone(data.get("phone")), str(data.get("password", ""))
        if not name or not email or "@" not in email:
            return jsonify({"error": "Name and valid email are required"}), 400
        if not valid_phone(phone):
            return jsonify({"error": "Use mobile number with country code, e.g. +919876543210"}), 400
        if len(password) < 8 or len(password) > 128:
            return jsonify({"error": "Password must be 8 to 128 characters"}), 400
        if User.query.filter_by(email=email).first() or AccountSecurity.query.filter_by(phone_number=phone).first():
            return jsonify({"error": "Unable to create account"}), 409
        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.flush()
        state = AccountSecurity(user_id=user.id, phone_number=phone)
        db.session.add(state)
        db.session.commit()
        for purpose, channel, destination in (("email_verification", "email", email), ("mobile_verification", "sms", phone)):
            try:
                issue_code(user, purpose, channel, destination)
            except Exception:
                app.logger.exception("Verification delivery failed")
        return jsonify({"email": email, "phone": phone, "verification_required": True}), 201

    @app.post("/api/product-auth/resend")
    @limiter.limit("3 per 10 minutes")
    def resend_codes():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            state = _state(user)
            try:
                if not state.email_verified: issue_code(user, "email_verification", "email", user.email)
                if state.phone_number and not state.mobile_verified: issue_code(user, "mobile_verification", "sms", state.phone_number)
            except Exception:
                app.logger.exception("Resend delivery failed")
        return jsonify({"message": "Verification codes processed."})

    @app.post("/api/product-auth/verify-email")
    @limiter.limit("10 per minute")
    def verify_email():
        data = request.get_json(silent=True) or {}
        user = User.query.filter_by(email=str(data.get("email", "")).strip().lower()).first()
        if not user or not verify_code(user, "email_verification", "email", data.get("code")):
            return jsonify({"error": "Invalid or expired email verification code"}), 400
        _state(user).email_verified = True
        db.session.commit()
        return jsonify({"verified": True})

    @app.post("/api/product-auth/verify-mobile")
    @limiter.limit("10 per minute")
    def verify_mobile():
        data = request.get_json(silent=True) or {}
        phone = normalize_phone(data.get("phone"))
        state = AccountSecurity.query.filter_by(phone_number=phone).first()
        user = db.session.get(User, state.user_id) if state else None
        if not user or not verify_code(user, "mobile_verification", "sms", data.get("code")):
            return jsonify({"error": "Invalid or expired mobile verification code"}), 400
        state.mobile_verified = True
        db.session.commit()
        return jsonify({"verified": True})

    @app.post("/api/product-auth/login")
    @limiter.limit("5 per minute")
    def product_login():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user or not user.password_hash or not check_password_hash(user.password_hash, str(data.get("password", ""))):
            return jsonify({"error": "Invalid email or password"}), 401
        state = _state(user)
        if not state.email_verified or not state.mobile_verified:
            return jsonify({"error": "Verify your email and mobile number first", "verification_required": True}), 403
        if state.two_factor_enabled:
            destination = user.email if state.two_factor_channel == "email" else state.phone_number
            issue_code(user, "login_2fa", state.two_factor_channel, destination)
            return jsonify({"two_factor_required": True, "channel": state.two_factor_channel, "expires_in": OTP_TTL_MINUTES * 60})
        return jsonify({"access_token": _token(user), "token_type": "Bearer", "expires_in": 43200})

    @app.post("/api/product-auth/2fa/verify")
    @limiter.limit("10 per minute")
    def verify_login_2fa():
        data = request.get_json(silent=True) or {}
        user = User.query.filter_by(email=str(data.get("email", "")).strip().lower()).first()
        state = _state(user) if user else None
        if not user or not state or not state.two_factor_enabled or not verify_code(user, "login_2fa", state.two_factor_channel, data.get("code")):
            return jsonify({"error": "Invalid or expired two-factor code"}), 401
        return jsonify({"access_token": _token(user), "token_type": "Bearer", "expires_in": 43200})

    @app.post("/api/product-auth/2fa/setup")
    @_protected
    def setup_2fa():
        data = request.get_json(silent=True) or {}
        state = _state(request.current_user)
        if not state.email_verified or not state.mobile_verified:
            return jsonify({"error": "Verify both email and mobile before enabling 2FA"}), 400
        channel = str(data.get("channel", "email")).lower()
        if channel not in {"email", "sms"}:
            return jsonify({"error": "Channel must be email or sms"}), 400
        state.two_factor_channel = channel
        db.session.commit()
        destination = request.current_user.email if channel == "email" else state.phone_number
        issue_code(request.current_user, "login_2fa", channel, destination)
        return jsonify({"message": "2FA setup code sent", "channel": channel})

    @app.post("/api/product-auth/2fa/enable")
    @_protected
    def enable_2fa():
        state = _state(request.current_user)
        code = (request.get_json(silent=True) or {}).get("code")
        if not verify_code(request.current_user, "login_2fa", state.two_factor_channel, code):
            return jsonify({"error": "Invalid or expired 2FA setup code"}), 400
        state.two_factor_enabled = True
        db.session.commit()
        return jsonify({"two_factor_enabled": True, "channel": state.two_factor_channel})

    @app.post("/api/product-auth/2fa/disable")
    @_protected
    def disable_2fa():
        _state(request.current_user).two_factor_enabled = False
        db.session.commit()
        return jsonify({"two_factor_enabled": False})

    @app.get("/api/product-auth/security-status")
    @_protected
    def security_status():
        state = _state(request.current_user)
        return jsonify({"email_verified": state.email_verified, "mobile_verified": state.mobile_verified, "two_factor_enabled": state.two_factor_enabled, "two_factor_channel": state.two_factor_channel})
