"""Persistent scan history for the Streamlit product experience.

Uses hosted PostgreSQL when DATABASE_URL is configured and SQLite otherwise.
This layer is intentionally separate from the existing Flask scan database so
the Streamlit-native authentication flow can work without Render.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return str(value or os.getenv(name, default) or "").strip()


def database_url() -> str:
    return _secret("DATABASE_URL")


def _normalized_postgres_url() -> str:
    url = database_url()
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url[len("postgresql+psycopg://"):]
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def _is_postgres() -> bool:
    return _normalized_postgres_url().lower().startswith("postgresql://")


def _connect():
    if _is_postgres():
        import psycopg
        return psycopg.connect(_normalized_postgres_url())
    db_path = Path(_secret("SQLITE_PATH", "instance/streamlit_auth.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path), check_same_thread=False)


def _placeholder() -> str:
    return "%s" if _is_postgres() else "?"


def ensure_schema() -> None:
    with _connect() as conn:
        if _is_postgres():
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS streamlit_scan_history (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT,
                    session_key VARCHAR(128) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    prediction VARCHAR(255),
                    confidence REAL,
                    status VARCHAR(30) NOT NULL,
                    top_predictions TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_streamlit_scan_history_user
                ON streamlit_scan_history(user_id, created_at DESC)
                """
            )
        else:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS streamlit_scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_key TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    prediction TEXT,
                    confidence REAL,
                    status TEXT NOT NULL,
                    top_predictions TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_streamlit_scan_history_user
                ON streamlit_scan_history(user_id, created_at DESC)
                """
            )
        conn.commit()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_session_key(file_bytes: bytes, filename: str, prediction: str | None = None) -> str:
    payload = file_bytes + b"\0" + str(filename).encode("utf-8") + b"\0" + str(prediction or "").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def save_scan(
    *,
    user_id: int | None,
    session_key: str,
    filename: str,
    prediction: str | None,
    confidence: float | None,
    status: str,
    top_predictions: list[dict[str, Any]] | None = None,
) -> int | None:
    ensure_schema()
    encoded_top = json.dumps(top_predictions or [], ensure_ascii=False)
    with _connect() as conn:
        cur = conn.cursor()
        ph = _placeholder()

        existing = cur.execute(
            f"SELECT id FROM streamlit_scan_history WHERE session_key = {ph} LIMIT 1",
            (session_key,),
        ).fetchone()
        if existing:
            return int(existing[0])

        if _is_postgres():
            row = cur.execute(
                """
                INSERT INTO streamlit_scan_history
                (user_id, session_key, filename, prediction, confidence, status, top_predictions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, session_key, filename, prediction, confidence, status, encoded_top),
            ).fetchone()
            conn.commit()
            return int(row[0])
        cur.execute(
            """
            INSERT INTO streamlit_scan_history
            (user_id, session_key, filename, prediction, confidence, status, top_predictions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, session_key, filename, prediction, confidence, status, encoded_top, _now_iso()),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_scans(user_id: int | None, limit: int = 50) -> list[dict[str, Any]]:
    ensure_schema()
    limit = max(1, min(int(limit), 200))
    ph = _placeholder()

    with _connect() as conn:
        cur = conn.cursor()
        if user_id is None:
            rows = cur.execute(
                f"""
                SELECT id, filename, prediction, confidence, status, top_predictions, created_at
                FROM streamlit_scan_history
                WHERE user_id IS NULL
                ORDER BY created_at DESC
                LIMIT {ph}
                """,
                (limit,),
            ).fetchall()
        else:
            rows = cur.execute(
                f"""
                SELECT id, filename, prediction, confidence, status, top_predictions, created_at
                FROM streamlit_scan_history
                WHERE user_id = {ph}
                ORDER BY created_at DESC
                LIMIT {ph}
                """,
                (user_id, limit),
            ).fetchall()

    result = []
    for row in rows:
        try:
            top_predictions = json.loads(row[5] or "[]")
        except Exception:
            top_predictions = []
        result.append(
            {
                "id": int(row[0]),
                "filename": row[1],
                "prediction": row[2],
                "confidence": float(row[3]) if row[3] is not None else None,
                "status": row[4],
                "top_predictions": top_predictions,
                "created_at": row[6],
            }
        )
    return result


def dashboard_stats(scans: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [s for s in scans if s["status"] == "completed"]
    rejected = [s for s in scans if s["status"] != "completed"]
    confidences = [s["confidence"] for s in completed if s["confidence"] is not None]
    healthy = [
        s for s in completed
        if s["prediction"] and "healthy" in str(s["prediction"]).lower()
    ]
    disease = [s for s in completed if s not in healthy]

    return {
        "total": len(scans),
        "completed": len(completed),
        "rejected": len(rejected),
        "average_confidence": round(sum(confidences) / len(confidences), 2) if confidences else None,
        "healthy": len(healthy),
        "condition_detected": len(disease),
    }


def scans_to_csv(scans: list[dict[str, Any]]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Filename", "Prediction", "Confidence (%)", "Status", "Created At"])
    for scan in scans:
        writer.writerow(
            [
                scan["id"],
                scan["filename"],
                scan["prediction"] or "",
                scan["confidence"] if scan["confidence"] is not None else "",
                scan["status"],
                scan["created_at"],
            ]
        )
    return output.getvalue().encode("utf-8")
