"""Streamlit-side client for the Flask product authentication API."""
from __future__ import annotations

import os

import requests
import streamlit as st


def auth_base_url() -> str:
    try:
        value = st.secrets.get("PRODUCT_AUTH_API_URL", "")
    except Exception:
        value = ""
    return str(value or os.getenv("PRODUCT_AUTH_API_URL", "")).rstrip("/")


def api_post(path: str, payload: dict):
    base = auth_base_url()
    if not base:
        return None, {"error": "Authentication API is not configured. Set PRODUCT_AUTH_API_URL in Streamlit secrets/environment."}
    try:
        response = requests.post(f"{base}{path}", json=payload, timeout=15)
        try:
            data = response.json()
        except ValueError:
            data = {"error": "Authentication service returned an invalid response."}
        return response, data
    except requests.RequestException as exc:
        return None, {"error": f"Authentication service unavailable: {exc}"}


def authenticated_headers() -> dict:
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_get(path: str):
    base = auth_base_url()
    if not base:
        return None, {"error": "Authentication API is not configured."}
    try:
        response = requests.get(f"{base}{path}", headers=authenticated_headers(), timeout=15)
        try:
            data = response.json()
        except ValueError:
            data = {"error": "Authentication service returned an invalid response."}
        return response, data
    except requests.RequestException as exc:
        return None, {"error": f"Authentication service unavailable: {exc}"}
