"""Backward-compatible local auth adapter.

The public Streamlit pages historically called `api_post()` with Flask-style
paths. Those calls now execute the Streamlit-native auth engine locally, so no
Render URL, requests session, or external auth API is required.
"""
from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from streamlit_native_auth import (
    authenticate,
    create_user,
    get_user_by_email,
    get_user_by_identity,
    issue_otp,
    mark_email_verified,
    mark_mobile_verified,
    session_login,
    set_2fa_channel,
    set_2fa_enabled,
    verify_otp,
)


@dataclass
class LocalResponse:
    ok: bool
    status_code: int = 200


def _response(ok: bool, status_code: int = 200) -> LocalResponse:
    return LocalResponse(ok=ok, status_code=status_code)


def api_post(path: str, payload: dict):
    data = payload or {}

    if path == "/api/product-auth/register":
        user, error = create_user(data.get("name"), data.get("email"), data.get("phone"), data.get("password"))
        if error or not user:
            return _response(False, 400), {"error": error or "Unable to create account."}
        try:
            issue_otp(user["id"], "email_verification", "email", user["email"])
            issue_otp(user["id"], "mobile_verification", "sms", user["phone"])
        except Exception as exc:
            return _response(False, 500), {"error": f"Account created but verification delivery failed: {exc}"}
        return _response(True, 201), {"id": user["id"], "name": user["name"], "email": user["email"], "phone": user["phone"], "verification_required": True}

    if path == "/api/product-auth/login":
        identity = str(data.get("email", "")).strip()
        user, error = authenticate(identity, data.get("password", ""))
        if error == "verification_required" and user:
            return _response(False, 403), {
                "error": "Account verification required",
                "verification_required": True,
                "email_verified": user["email_verified"],
                "mobile_verified": user["mobile_verified"],
                "email": user["email"],
                "phone": user["phone"],
            }
        if error or not user:
            return _response(False, 401), {"error": error or "Login failed."}
        if user["two_factor_enabled"]:
            channel = user["two_factor_channel"] if user["two_factor_channel"] in {"email", "sms"} else "email"
            destination = user["email"] if channel == "email" else user["phone"]
            issue_otp(user["id"], "login_2fa", channel, destination)
            st.session_state["login_identity"] = identity
            return _response(True, 200), {"two_factor_required": True, "channel": channel, "expires_in": 600}
        session_login(user)
        return _response(True, 200), {"access_token": "streamlit-session", "token_type": "Session"}

    if path == "/api/product-auth/verify-email":
        user = get_user_by_email(data.get("email", ""))
        ok = bool(user and verify_otp(user["id"], "email_verification", data.get("code", ""), "email"))
        if ok:
            mark_email_verified(user["id"])
            return _response(True), {"verified": True, "email_verified": True}
        return _response(False, 400), {"error": "Invalid or expired verification code"}

    if path == "/api/product-auth/verify-mobile":
        phone = str(data.get("phone", "")).strip()
        user = get_user_by_identity(phone)
        ok = bool(user and verify_otp(user["id"], "mobile_verification", data.get("code", ""), "sms"))
        if ok:
            mark_mobile_verified(user["id"])
            return _response(True), {"verified": True, "mobile_verified": True}
        return _response(False, 400), {"error": "Invalid or expired verification code"}

    if path == "/api/product-auth/resend":
        user = get_user_by_email(data.get("email", ""))
        if not user:
            return _response(True), {"message": "If the account exists, verification codes have been processed."}
        if not user["email_verified"]:
            issue_otp(user["id"], "email_verification", "email", user["email"])
        if not user["mobile_verified"]:
            issue_otp(user["id"], "mobile_verification", "sms", user["phone"])
        return _response(True), {"message": "Verification codes have been regenerated."}

    if path == "/api/product-auth/2fa/verify":
        identity = str(data.get("email", "")).strip()
        user = get_user_by_identity(identity)
        channel = st.session_state.get("login_2fa_channel", user["two_factor_channel"] if user else "email")
        ok = bool(user and st.session_state.get("pending_2fa_user_id") == user["id"] and verify_otp(user["id"], "login_2fa", data.get("code", ""), channel))
        if ok:
            session_login(user)
            return _response(True), {"access_token": "streamlit-session", "token_type": "Session"}
        return _response(False, 401), {"error": "Invalid or expired two-factor code."}

    if path == "/api/product-auth/2fa/setup":
        user = st.session_state.get("auth_user")
        if not user:
            return _response(False, 401), {"error": "Authentication required"}
        channel = str(data.get("channel", "email")).lower()
        if channel not in {"email", "sms"}:
            return _response(False, 400), {"error": "Channel must be email or sms"}
        set_2fa_channel(user["id"], channel)
        destination = user["email"] if channel == "email" else user["phone"]
        issue_otp(user["id"], "two_factor_setup", channel, destination)
        return _response(True), {"message": "2FA setup code sent", "channel": channel}

    if path == "/api/product-auth/2fa/enable":
        user = st.session_state.get("auth_user")
        if not user:
            return _response(False, 401), {"error": "Authentication required"}
        channel = user["two_factor_channel"]
        if verify_otp(user["id"], "two_factor_setup", data.get("code", ""), channel):
            set_2fa_enabled(user["id"], True)
            return _response(True), {"two_factor_enabled": True, "channel": channel}
        return _response(False, 400), {"error": "Invalid or expired 2FA setup code"}

    return _response(False, 404), {"error": f"Unsupported local auth route: {path}"}


def authenticated_headers() -> dict:
    return {"Authorization": "Bearer streamlit-session"} if st.session_state.get("authenticated") else {}


def api_get(path: str):
    return _response(False, 404), {"error": f"GET auth route is not used by Streamlit-native auth: {path}"}
