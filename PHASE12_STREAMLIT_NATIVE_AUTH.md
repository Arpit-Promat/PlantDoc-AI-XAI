# Phase 12 — Streamlit-Native Authentication

The Streamlit application no longer depends on a Flask/Render authentication URL.

## Flow
Landing → Sign Up → Email Verification → Mobile Verification → Optional OTP 2FA → Login → AI Scanner

## Runtime dependencies
- Streamlit for the UI/session flow
- PostgreSQL via `DATABASE_URL` for persistent cloud users/challenges
- SQLite fallback for local development
- SMTP for email OTP delivery
- Twilio for SMS OTP delivery

## Streamlit secrets
```toml
DATABASE_URL = "postgresql://..."
SMTP_HOST = "smtp.example.com"
SMTP_PORT = "587"
SMTP_USE_TLS = "1"
SMTP_USERNAME = "..."
SMTP_PASSWORD = "..."
EMAIL_FROM = "..."
TWILIO_ACCOUNT_SID = "..."
TWILIO_AUTH_TOKEN = "..."
TWILIO_FROM_NUMBER = "+1..."
# AUTH_DEV_SHOW_OTP = "1"  # development/demo only
```

`PRODUCT_AUTH_API_URL` is no longer used by the Streamlit authentication flow.