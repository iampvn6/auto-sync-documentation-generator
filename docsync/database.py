import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_DB_PATH = Path("docsync.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    file_path TEXT NOT NULL,
    module_name TEXT NOT NULL,
    docs_file TEXT NOT NULL,
    status TEXT NOT NULL
);
"""


def _connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    return connection


def record_scan(
    file_path: str,
    module_name: str,
    docs_file: str,
    status: str,
    db_path: str | Path | None = None,
) -> int:
    """Insert a scan record and return its row id."""
    connection = _connect(db_path or DEFAULT_DB_PATH)

    try:
        cursor = connection.execute(
            "INSERT INTO scans (created_at, file_path, module_name, docs_file, status)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                datetime.now(UTC).isoformat(),
                file_path,
                module_name,
                docs_file,
                status,
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_scan(scan_id: int, db_path: str | Path | None = None) -> dict | None:
    """Return one scan record, or None when it doesn't exist."""
    connection = _connect(db_path or DEFAULT_DB_PATH)

    try:
        row = connection.execute(
            "SELECT * FROM scans WHERE id = ?",
            (scan_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def list_scans(limit: int = 20, db_path: str | Path | None = None) -> list[dict]:
    """Return the most recent scan records."""
    connection = _connect(db_path or DEFAULT_DB_PATH)

    try:
        rows = connection.execute(
            "SELECT * FROM scans ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
