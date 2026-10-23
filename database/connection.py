"""SQLite connection helpers. The database path can be overridden with MARKETING_OPS_DB."""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "marketing_ops.db"

def database_path():
    return Path(os.getenv("MARKETING_OPS_DB", str(DEFAULT_DB))).expanduser()

@contextmanager
def get_connection():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    schema_path = Path(__file__).with_name("schema.sql")
    with get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        # Lightweight forward-compatible migrations for beta schema changes.
        columns = {r["name"] for r in conn.execute("PRAGMA table_info(clients)")}
        if "website_status" not in columns:
            conn.execute("ALTER TABLE clients ADD COLUMN website_status TEXT NOT NULL DEFAULT 'Unknown'")
