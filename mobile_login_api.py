"""Mobile-number login adapter for the ATHARVADRISHTI product login form."""
from flask import jsonify, request
from werkzeug.security import check_password_hash

from database import db, User
from product_auth import AccountSecurity, issue_code, normalize_phone, _token
from security import limiter


def register_mobile_login_route(app):
    @app.post("/api/product-auth/mobile-login")
    @limiter.limit("5 per minute")
    def mobile_login():
        data = request.get_json(silent=True) or {}
        phone = normalize_phone(data.get("phone"))
        password = str(data.get("password", ""))
        state = AccountSecurity.query.filter_by(phone_number=phone).first()
        user = db.session.get(User, state.user_id) if state else None
        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid mobile number or password"}), 401
        state = AccountSecurity.query.filter_by(user_id=user.id).first()
        if not state or not state.email_verified or not state.mobile_verified:
            return jsonify({"error": "Verify your email and mobile number first", "verification_required": True}), 403
        if state.two_factor_enabled:
            destination = user.email if state.two_factor_channel == "email" else state.phone_number
            issue_code(user, "login_2fa", state.two_factor_channel, destination)
            return jsonify({"two_factor_required": True, "channel": state.two_factor_channel, "email": user.email, "expires_in": 600})
        return jsonify({"access_token": _token(user), "token_type": "Bearer", "expires_in": 43200})
