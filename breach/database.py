import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".breach" / "breach.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cache (
                number      INTEGER PRIMARY KEY,
                data_json   TEXT NOT NULL,
                cached_at   TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS favorites (
                number      INTEGER PRIMARY KEY,
                title       TEXT NOT NULL,
                object_class TEXT,
                note        TEXT,
                saved_at    TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                number      INTEGER NOT NULL,
                title       TEXT NOT NULL,
                accessed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS config (
                key         TEXT PRIMARY KEY,
                value       TEXT NOT NULL
            );
        """)
        # Default clearance level
        conn.execute(
            "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
            ("clearance_level", "5")
        )


# ── Cache ──────────────────────────────────────────────────────────────────────

def cache_get(number: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT data_json FROM cache WHERE number = ?", (number,)
        ).fetchone()
        return json.loads(row["data_json"]) if row else None


def cache_set(number: int, data: dict):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache (number, data_json, cached_at) VALUES (?, ?, ?)",
            (number, json.dumps(data), datetime.utcnow().isoformat())
        )


# ── History ────────────────────────────────────────────────────────────────────

def history_add(number: int, title: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO history (number, title, accessed_at) VALUES (?, ?, ?)",
            (number, title, datetime.utcnow().isoformat())
        )


def history_get(limit: int = 20) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT number, title, accessed_at FROM history ORDER BY accessed_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def history_clear():
    with get_connection() as conn:
        conn.execute("DELETE FROM history")


# ── Favorites ──────────────────────────────────────────────────────────────────

def favorite_add(number: int, title: str, object_class: str, note: str = ""):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO favorites (number, title, object_class, note, saved_at) VALUES (?, ?, ?, ?, ?)",
            (number, title, object_class, note, datetime.utcnow().isoformat())
        )


def favorite_remove(number: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM favorites WHERE number = ?", (number,))


def favorite_get_all() -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM favorites ORDER BY saved_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def favorite_exists(number: int) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM favorites WHERE number = ?", (number,)
        ).fetchone()
        return row is not None


# ── Config ─────────────────────────────────────────────────────────────────────

def config_get(key: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None


def config_set(key: str, value: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, value)
        )

