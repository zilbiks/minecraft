import hashlib
import hmac
import os
import sqlite3
from datetime import date
from typing import Optional, Set


DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
PBKDF2_ITERATIONS = 200_000


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
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf8"),
        bytes.fromhex(salt),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith("pbkdf2_sha256$"):
        try:
            _, iterations_raw, salt, expected = stored_hash.split("$", 3)
            iterations = int(iterations_raw)
        except (ValueError, TypeError):
            return False
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            (password or "").encode("utf8"),
            bytes.fromhex(salt),
            iterations,
        ).hex()
        return hmac.compare_digest(computed, expected)

    legacy_hash = hashlib.sha256((password or "").encode("utf8")).hexdigest()
    return hmac.compare_digest(legacy_hash, stored_hash)


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
    with connect() as con:
        row = con.execute(
            "SELECT id, password_hash FROM users WHERE username = ?;",
            (username,),
        ).fetchone()
    if not row:
        return None

    user_id, stored_hash = int(row[0]), str(row[1])
    if verify_password(password or "", stored_hash):
        return user_id
    return None


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


def get_solved_activity_dates(user_id: int) -> Set[date]:
    with connect() as con:
        rows = con.execute(
            "SELECT DISTINCT date(solved_at) FROM solved WHERE user_id = ?;",
            (int(user_id),),
        ).fetchall()

    parsed: Set[date] = set()
    for row in rows:
        raw = row[0]
        if not raw:
            continue
        try:
            parsed.add(date.fromisoformat(str(raw)))
        except ValueError:
            continue
    return parsed
