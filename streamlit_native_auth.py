"""Streamlit-native authentication for ATHARVADRISHTRI.

No Flask/Render dependency is used by the Streamlit login flow.
For deployed persistence, configure DATABASE_URL to a hosted PostgreSQL database.
Local development can use SQLITE_PATH (default: instance/streamlit_auth.db).
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
import smtplib
import sqlite3
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash

OTP_TTL_MINUTES = 10
MAX_OTP_ATTEMPTS = 5
OTP_LENGTH = 6
PHONE_RE = re.compile(r"^\+?[1-9]\d{9,14}$")


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return str(value or os.getenv(name, default) or "").strip()


def database_url() -> str:
    return _secret("DATABASE_URL")


def _is_postgres() -> bool:
    url = database_url().lower()
    return url.startswith("postgres://") or url.startswith("postgresql://")


def _connect():
    if _is_postgres():
        import psycopg
        return psycopg.connect(database_url())
    db_path = Path(_secret("SQLITE_PATH", "instance/streamlit_auth.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path), check_same_thread=False)


def _placeholder() -> str:
    return "%s" if _is_postgres() else "?"


def _bool_value(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def ensure_schema() -> None:
    with _connect() as conn:
        if _is_postgres():
            conn.execute("""
                CREATE TABLE IF NOT EXISTS streamlit_users (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(120) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    phone VARCHAR(32) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    mobile_verified BOOLEAN NOT NULL DEFAULT FALSE,
                    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    two_factor_channel VARCHAR(12) NOT NULL DEFAULT 'email',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS streamlit_auth_challenges (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES streamlit_users(id) ON DELETE CASCADE,
                    purpose VARCHAR(30) NOT NULL,
                    channel VARCHAR(12) NOT NULL,
                    destination VARCHAR(255) NOT NULL,
                    code_hash VARCHAR(255) NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    used_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        else:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS streamlit_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    email_verified INTEGER NOT NULL DEFAULT 0,
                    mobile_verified INTEGER NOT NULL DEFAULT 0,
                    two_factor_enabled INTEGER NOT NULL DEFAULT 0,
                    two_factor_channel TEXT NOT NULL DEFAULT 'email',
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS streamlit_auth_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    purpose TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    used_at TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES streamlit_users(id) ON DELETE CASCADE
                )
            """)
        conn.commit()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_phone(phone: str) -> str:
    value = str(phone or "").strip().replace(" ", "")
    if value.startswith("00"):
        value = "+" + value[2:]
    return value


def valid_phone(phone: str) -> bool:
    return bool(PHONE_RE.fullmatch(phone or ""))


def normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def _row_to_user(row) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": int(row[0]),
        "name": row[1],
        "email": row[2],
        "phone": row[3],
        "password_hash": row[4],
        "email_verified": bool(row[5]),
        "mobile_verified": bool(row[6]),
        "two_factor_enabled": bool(row[7]),
        "two_factor_channel": row[8],
    }


def get_user_by_identity(identity: str) -> dict[str, Any] | None:
    ensure_schema()
    email = normalize_email(identity)
    phone = normalize_phone(identity)
    ph = _placeholder()
    with _connect() as conn:
        row = conn.execute(
            f"SELECT id,name,email,phone,password_hash,email_verified,mobile_verified,two_factor_enabled,two_factor_channel FROM streamlit_users WHERE email={ph} OR phone={ph}",
            (email, phone),
        ).fetchone()
    return _row_to_user(row)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    return get_user_by_identity(email)


def create_user(name: str, email: str, phone: str, password: str) -> tuple[dict[str, Any] | None, str | None]:
    ensure_schema()
    name = str(name or "").strip()
    email = normalize_email(email)
    phone = normalize_phone(phone)
    if not name or len(name) > 120:
        return None, "Name is required."
    if "@" not in email or len(email) > 255:
        return None, "Enter a valid email address."
    if not valid_phone(phone):
        return None, "Enter a valid mobile number with country code, for example +919876543210."
    if len(password) < 8 or len(password) > 128:
        return None, "Password must be 8 to 128 characters."

    ph = _placeholder()
    created_at = _now().isoformat()
    try:
        with _connect() as conn:
            existing = conn.execute(
                f"SELECT id FROM streamlit_users WHERE email={ph} OR phone={ph}",
                (email, phone),
            ).fetchone()
            if existing:
                return None, "An account with this email or mobile number already exists."
            if _is_postgres():
                row = conn.execute(
                    f"INSERT INTO streamlit_users (name,email,phone,password_hash) VALUES ({ph},{ph},{ph},{ph}) RETURNING id,name,email,phone,password_hash,email_verified,mobile_verified,two_factor_enabled,two_factor_channel",
                    (name, email, phone, generate_password_hash(password)),
                ).fetchone()
            else:
                conn.execute(
                    f"INSERT INTO streamlit_users (name,email,phone,password_hash,email_verified,mobile_verified,two_factor_enabled,two_factor_channel,created_at) VALUES ({ph},{ph},{ph},{ph},0,0,0,'email',{ph})",
                    (name, email, phone, generate_password_hash(password), created_at),
                )
                user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                row = conn.execute("SELECT id,name,email,phone,password_hash,email_verified,mobile_verified,two_factor_enabled,two_factor_channel FROM streamlit_users WHERE id=?", (user_id,)).fetchone()
            conn.commit()
    except Exception as exc:
        return None, f"Could not create account: {exc}"
    return _row_to_user(row), None


def _hash_otp(code: str) -> str:
    salt = _secret("OTP_HASH_SALT", "atharvadrishti-dev-salt")
    return hashlib.sha256(f"{salt}:{code}".encode()).hexdigest()


def _make_otp() -> str:
    return f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"


def _deliver_email(destination: str, subject: str, body: str) -> None:
    host = _secret("SMTP_HOST")
    if not host:
        print(f"ATHARVADRISHTRI EMAIL DEV FALLBACK -> {destination}: {body}")
        return
    port = int(_secret("SMTP_PORT", "587"))
    username = _secret("SMTP_USERNAME")
    password = _secret("SMTP_PASSWORD")
    sender = _secret("EMAIL_FROM", username or "no-reply@atharvadrishti.local")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = destination
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(host, port, timeout=15) as smtp:
        if _secret("SMTP_USE_TLS", "1") == "1":
            smtp.starttls()
        if username:
            smtp.login(username, password)
        smtp.send_message(message)


def _deliver_sms(destination: str, body: str) -> None:
    sid = _secret("TWILIO_ACCOUNT_SID")
    token = _secret("TWILIO_AUTH_TOKEN")
    from_number = _secret("TWILIO_FROM_NUMBER")
    if not (sid and token and from_number):
        print(f"ATHARVADRISHTRI SMS DEV FALLBACK -> {destination}: {body}")
        return
    from twilio.rest import Client
    Client(sid, token).messages.create(body=body, from_=from_number, to=destination)


def issue_otp(user_id: int, purpose: str, channel: str, destination: str) -> str:
    ensure_schema()
    code = _make_otp()
    ph = _placeholder()
    created_at = _now()
    expires_at = created_at + timedelta(minutes=OTP_TTL_MINUTES)
    with _connect() as conn:
        conn.execute(
            f"UPDATE streamlit_auth_challenges SET used_at={ph} WHERE user_id={ph} AND purpose={ph} AND used_at IS NULL",
            (created_at.isoformat(), user_id, purpose),
        )
        conn.execute(
            f"INSERT INTO streamlit_auth_challenges (user_id,purpose,channel,destination,code_hash,expires_at,attempts,created_at) VALUES ({ph},{ph},{ph},{ph},{ph},{ph},0,{ph})",
            (user_id, purpose, channel, destination, _hash_otp(code), expires_at.isoformat(), created_at.isoformat()),
        )
        conn.commit()

    subject = {
        "email_verification": "Verify your ATHARVADRISHTRI email",
        "mobile_verification": "Verify your ATHARVADRISHTRI mobile number",
        "login_2fa": "Your ATHARVADRISHTRI security code",
        "two_factor_setup": "Set up ATHARVADRISHTRI two-factor authentication",
    }.get(purpose, "Your ATHARVADRISHTRI verification code")
    body = f"Your ATHARVADRISHTRI verification code is {code}. It expires in {OTP_TTL_MINUTES} minutes."
    if channel == "email":
        _deliver_email(destination, subject, body)
    else:
        _deliver_sms(destination, body)
    if _secret("AUTH_DEV_SHOW_OTP", "0") == "1":
        st.session_state["dev_last_otp"] = code
    return code


def verify_otp(user_id: int, purpose: str, code: str, channel: str | None = None) -> bool:
    ensure_schema()
    ph = _placeholder()
    with _connect() as conn:
        if channel:
            row = conn.execute(
                f"SELECT id,code_hash,expires_at,attempts FROM streamlit_auth_challenges WHERE user_id={ph} AND purpose={ph} AND channel={ph} AND used_at IS NULL ORDER BY created_at DESC LIMIT 1",
                (user_id, purpose, channel),
            ).fetchone()
        else:
            row = conn.execute(
                f"SELECT id,code_hash,expires_at,attempts FROM streamlit_auth_challenges WHERE user_id={ph} AND purpose={ph} AND used_at IS NULL ORDER BY created_at DESC LIMIT 1",
                (user_id, purpose),
            ).fetchone()
        if row is None:
            return False
        challenge_id, code_hash, expires_at_raw, attempts = row
        if isinstance(expires_at_raw, datetime):
            expires_at = expires_at_raw if expires_at_raw.tzinfo else expires_at_raw.replace(tzinfo=timezone.utc)
        else:
            expires_at = datetime.fromisoformat(str(expires_at_raw).replace("Z", "+00:00"))
        if expires_at < _now() or int(attempts or 0) >= MAX_OTP_ATTEMPTS:
            return False
        conn.execute(f"UPDATE streamlit_auth_challenges SET attempts=attempts+1 WHERE id={ph}", (challenge_id,))
        if not secrets.compare_digest(code_hash, _hash_otp(str(code or ""))):
            conn.commit()
            return False
        conn.execute(f"UPDATE streamlit_auth_challenges SET used_at={ph} WHERE id={ph}", (_now().isoformat(), challenge_id))
        conn.commit()
        return True


def mark_email_verified(user_id: int) -> None:
    ph = _placeholder()
    value = "TRUE" if _is_postgres() else "1"
    with _connect() as conn:
        conn.execute(f"UPDATE streamlit_users SET email_verified={value} WHERE id={ph}", (user_id,))
        conn.commit()


def mark_mobile_verified(user_id: int) -> None:
    ph = _placeholder()
    value = "TRUE" if _is_postgres() else "1"
    with _connect() as conn:
        conn.execute(f"UPDATE streamlit_users SET mobile_verified={value} WHERE id={ph}", (user_id,))
        conn.commit()


def set_2fa_channel(user_id: int, channel: str) -> None:
    ph = _placeholder()
    with _connect() as conn:
        conn.execute(f"UPDATE streamlit_users SET two_factor_channel={ph} WHERE id={ph}", (channel, user_id))
        conn.commit()


def set_2fa_enabled(user_id: int, enabled: bool) -> None:
    ph = _placeholder()
    value = _bool_value(enabled) if _is_postgres() else ("1" if enabled else "0")
    with _connect() as conn:
        conn.execute(f"UPDATE streamlit_users SET two_factor_enabled={value} WHERE id={ph}", (user_id,))
        conn.commit()


def authenticate(identity: str, password: str) -> tuple[dict[str, Any] | None, str | None]:
    user = get_user_by_identity(identity)
    if not user or not check_password_hash(user["password_hash"], str(password or "")):
        return None, "Invalid email/mobile number or password."
    if not user["email_verified"] or not user["mobile_verified"]:
        return user, "verification_required"
    return user, None


def session_login(user: dict[str, Any]) -> None:
    st.session_state["authenticated"] = True
    st.session_state["auth_user_id"] = user["id"]
    st.session_state["auth_user"] = user
    st.session_state.pop("pending_2fa_user_id", None)
    st.session_state.pop("login_2fa_channel", None)


def session_logout() -> None:
    for key in ["authenticated", "auth_user_id", "auth_user", "pending_2fa_user_id", "login_2fa_channel", "dev_last_otp"]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated") and st.session_state.get("auth_user_id"))


def current_user() -> dict[str, Any] | None:
    return st.session_state.get("auth_user")
