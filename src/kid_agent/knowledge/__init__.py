"""Knowledge module — manages the K-12 knowledge database."""

from pathlib import Path
import os
import sqlite3

_KB_DIR = Path(os.environ.get(
    "KID_KB_DIR",
    str(Path(__file__).resolve().parent.parent.parent.parent / "data"),
))
_KB_PATH = _KB_DIR / "knowledge.db"


def get_kb_path() -> Path:
    """Return the path to the knowledge database."""
    return _KB_PATH


def get_kb_conn() -> sqlite3.Connection:
    """Get a connection to the knowledge database."""
    if not _KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge database not found: {_KB_PATH}")
    conn = sqlite3.connect(str(_KB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_kb_stats() -> dict:
    """Return statistics about the knowledge base."""
    conn = get_kb_conn()
    try:
        concepts = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        relations = conn.execute("SELECT COUNT(*) FROM relation_prerequisite").fetchone()[0]
        mistakes = conn.execute("SELECT COUNT(*) FROM common_mistakes").fetchone()[0]
        books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        return {
            "concepts": concepts,
            "relations": relations,
            "mistakes": mistakes,
            "books": books,
            "path": str(_KB_PATH),
        }
    finally:
        conn.close()


__all__ = ["get_kb_path", "get_kb_conn", "get_kb_stats"]
