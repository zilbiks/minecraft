import hashlib
import os
import sqlite3
from dataclasses import dataclass
from typing import Optional, Set


DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def init_db() -> None:
    with connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS solved (
                user_id INTEGER NOT NULL,
                title_slug TEXT NOT NULL,
                solved_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, title_slug),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf8")).hexdigest()

def create_user(username: str, password: str) -> tuple[bool, str]:
    username = (username or "").strip()
    if len(username) < 3:
        return False, "lietotajvardam jabut vismaz 3 simboli"
    if len(password or "") < 4:
        return False, "parolei jabut vismaz 4 simboli"

    pw_hash = hash_password(password)
    try:
        with connect() as con:
            con.execute(
                "INSERT INTO users(username, password_hash) VALUES(?, ?);",
                (username, pw_hash),
            )
        return True, "konts izveidots"
    except sqlite3.IntegrityError:
        return False, "sads lietotajvards jau eksiste"


def authenticate_user(username: str, password: str) -> Optional[int]:
    username = (username or "").strip()
    pw_hash = hash_password(password or "")
    with connect() as con:
        row = con.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?;",
            (username, pw_hash),
        ).fetchone()
    return int(row[0]) if row else None


def get_solved(user_id: int) -> Set[str]:
    with connect() as con:
        rows = con.execute(
            "SELECT title_slug FROM solved WHERE user_id = ?;",
            (int(user_id),),
        ).fetchall()
    return {str(r[0]) for r in rows}


def mark_solved(user_id: int, title_slug: str) -> None:
    if not title_slug:
        return
    with connect() as con:
        con.execute(
            "INSERT OR IGNORE INTO solved(user_id, title_slug) VALUES(?, ?);",
            (int(user_id), str(title_slug)),
        )
