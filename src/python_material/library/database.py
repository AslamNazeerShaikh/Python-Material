"""SQLite bootstrap: schema, relationships, indexes, and embedded seed data.

The schema demonstrates all three relationship shapes:

- 1:1 — ``authors`` to ``author_profiles`` (UNIQUE foreign key).
- 1:many — ``authors`` to ``books`` (plain foreign key + index).
- many:many — ``books`` to ``genres`` through ``book_genres``.

Indexes: PRIMARY KEY and UNIQUE constraints index themselves; the
three explicit CREATE INDEX statements cover the foreign-key and
filter columns the queries actually use (see docs/learning/14).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "library.db"

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS author_profiles (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL UNIQUE REFERENCES authors (id) ON DELETE CASCADE,
    bio TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    year INTEGER NOT NULL,
    author_id INTEGER NOT NULL REFERENCES authors (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS book_genres (
    book_id INTEGER NOT NULL REFERENCES books (id) ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES genres (id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);

CREATE INDEX IF NOT EXISTS idx_books_author ON books (author_id);
CREATE INDEX IF NOT EXISTS idx_books_year ON books (year);
CREATE INDEX IF NOT EXISTS idx_book_genres_genre ON book_genres (genre_id);
"""

# Embedded seed rows: (name, email) triples for authors.
_SEED_AUTHORS = [
    ("Ada Lovelace", "ada@example.com"),
    ("Grace Hopper", "grace@example.com"),
    ("Alan Turing", "alan@example.com"),
]

# Embedded seed rows: author name to bio. Alan ships WITHOUT a profile
# so reads demonstrate the optional side of the 1:1 link (LEFT JOIN).
_SEED_PROFILES = {
    "Ada Lovelace": "Wrote notes on the Analytical Engine.",
    "Grace Hopper": "Built the first compiler.",
}

# Embedded seed rows: genre names (UNIQUE, reused across books).
_SEED_GENRES = ["Science Fiction", "Essay", "Memoir", "Mathematics"]

# Embedded seed rows: (title, year, author name, genre names).
_SEED_BOOKS = [
    ("Notes on the Engine", 1843, "Ada Lovelace", ["Mathematics", "Essay"]),
    ("Sketch Collection", 1842, "Ada Lovelace", ["Memoir"]),
    ("Compiler Tales", 1952, "Grace Hopper", ["Memoir", "Essay"]),
    ("On Computable Numbers", 1936, "Alan Turing", ["Mathematics"]),
    ("Machine Intelligence", 1950, "Alan Turing", ["Science Fiction", "Essay"]),
]


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a hardened connection to the library database.

    Args:
        path: Database file. Parent directories are created on demand.

    Returns:
        Connection with Row factory and foreign keys enforced.
    """
    if path is None:
        raise ValueError("path must not be None")

    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables and indexes if missing (safe to rerun).

    Args:
        conn: Open connection to initialize.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    conn.executescript(SCHEMA)
    conn.commit()


def is_seeded(conn: sqlite3.Connection) -> bool:
    """Return True once any author row exists (seed exactly once).

    Args:
        conn: Open connection to inspect.

    Returns:
        True when the seed already ran, else False.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    row = conn.execute("SELECT COUNT(*) AS n FROM authors").fetchone()

    return bool(row["n"] > 0)


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Insert the embedded seed rows, skipping when already seeded.

    Args:
        conn: Open, initialized connection to seed.

    Returns:
        Counts per table actually inserted (zeros when skipped).
    """
    if conn is None:
        raise ValueError("conn must not be None")

    if is_seeded(conn):
        return {"authors": 0, "profiles": 0, "genres": 0, "books": 0}

    # Authors first: every later row keys off these ids.
    author_ids: dict[str, int] = {}
    for name, email in _SEED_AUTHORS:
        cur = conn.execute(
            "INSERT INTO authors (name, email, created_at) "
            "VALUES (?, ?, datetime('now'))",
            (name, email),
        )
        assert cur.lastrowid is not None
        author_ids[name] = cur.lastrowid

    # Profiles second: UNIQUE author_id enforces the 1:1 shape on write.
    for name, bio in _SEED_PROFILES.items():
        conn.execute(
            "INSERT INTO author_profiles (author_id, bio) VALUES (?, ?)",
            (author_ids[name], bio),
        )

    # Genres third: UNIQUE names make repeats collapse into one row.
    genre_ids: dict[str, int] = {}
    for name in _SEED_GENRES:
        cur = conn.execute("INSERT INTO genres (name) VALUES (?)", (name,))
        assert cur.lastrowid is not None
        genre_ids[name] = cur.lastrowid

    # Books last: each link row fans out into the m:m junction table.
    for title, year, author_name, genre_names in _SEED_BOOKS:
        cur = conn.execute(
            "INSERT INTO books (title, year, author_id) VALUES (?, ?, ?)",
            (title, year, author_ids[author_name]),
        )
        conn.executemany(
            "INSERT OR IGNORE INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [(cur.lastrowid, genre_ids[g]) for g in genre_names],
        )

    conn.commit()

    return {
        "authors": len(_SEED_AUTHORS),
        "profiles": len(_SEED_PROFILES),
        "genres": len(_SEED_GENRES),
        "books": len(_SEED_BOOKS),
    }


def reset_database(path: Path = DB_PATH) -> Path:
    """Rebuild a database file from scratch (delete, init, seed).

    Args:
        path: Database file to rebuild. Used to regenerate the
            committed seed database and by demos holding temp copies.

    Returns:
        The rebuilt path, for chaining.
    """
    if path is None:
        raise ValueError("path must not be None")

    # Sidecars (-wal/-shm) die with the main file: one glob-free sweep.
    for suffix in ("", "-wal", "-shm", "-journal"):
        sidecar = Path(str(path) + suffix)
        if sidecar.exists():
            sidecar.unlink()

    conn = connect(path)
    try:
        init_db(conn)
        seed(conn)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.commit()
    finally:
        conn.close()

    return path
