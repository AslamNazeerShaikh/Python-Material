"""CRUD over authors, profiles, books, and genres (pure SQL, no web)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from python_material.library.errors import (
    ConflictError,
    LibraryError,
    NotFoundError,
)
from python_material.library.models import (
    Author,
    AuthorDetail,
    AuthorProfile,
    Book,
    BookDetail,
    Genre,
)


def _utcnow() -> str:
    """Return the current UTC timestamp in ISO format (naive forbidden)."""
    return datetime.now(timezone.utc).isoformat()


def _like_escape(text: str) -> str:
    """Escape LIKE wildcards so user search text matches literally."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def create_author(conn: sqlite3.Connection, name: str, email: str) -> Author:
    """Insert one author, returning the stored snapshot.

    Args:
        conn: Open connection.
        name: Display name (must not be empty).
        email: Unique contact address (must not be empty).

    Returns:
        The inserted author, id included.

    Raises:
        ValueError: If a field is empty.
        ConflictError: If the email is taken.
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if not name:
        raise ValueError("name must not be empty")
    if not email:
        raise ValueError("email must not be empty")

    try:
        cur = conn.execute(
            "INSERT INTO authors (name, email, created_at) VALUES (?, ?, ?)",
            (name, email, _utcnow()),
        )
    except sqlite3.IntegrityError as exc:
        raise ConflictError(f"email {email!r} is already taken") from exc
    conn.commit()

    assert cur.lastrowid is not None
    author = get_author(conn, cur.lastrowid)
    if author is None:
        raise LibraryError("author insert succeeded but read-back failed")

    return author


def create_authors_bulk(
    conn: sqlite3.Connection, rows: list[tuple[str, str]]
) -> list[Author]:
    """Insert many authors in one round trip (executemany + one read).

    Args:
        conn: Open connection.
        rows: (name, email) pairs. Must not be empty.

    Returns:
        Inserted authors in input order.

    Raises:
        ValueError: If rows is empty or has blanks.
        ConflictError: If any email is taken (whole batch rolls back).
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if not rows:
        raise ValueError("rows must not be empty")
    if any(not name or not email for name, email in rows):
        raise ValueError("every row needs a name and an email")

    stamped = [(name, email, _utcnow()) for name, email in rows]
    try:
        conn.executemany(
            "INSERT INTO authors (name, email, created_at) VALUES (?, ?, ?)",
            stamped,
        )
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise ConflictError("bulk insert hit a taken email; rolled back") from exc
    conn.commit()

    # One read-back by the UNIQUE emails restores ids in input order.
    slots = ",".join("?" * len(rows))
    by_email = {
        row["email"]: Author.from_row(row)
        for row in conn.execute(
            f"SELECT * FROM authors WHERE email IN ({slots})",
            [email for _, email in rows],
        )
    }

    return [by_email[email] for _, email in rows]


def get_author(conn: sqlite3.Connection, author_id: int) -> Author | None:
    """Return one author by id, else None (no exception for absence).

    Args:
        conn: Open connection.
        author_id: Primary key to look up.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    row = conn.execute("SELECT * FROM authors WHERE id = ?", (author_id,)).fetchone()

    return Author.from_row(row) if row else None


def list_authors(conn: sqlite3.Connection) -> list[Author]:
    """Return every author ordered by id (stable listing).

    Args:
        conn: Open connection.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    return [
        Author.from_row(row)
        for row in conn.execute("SELECT * FROM authors ORDER BY id")
    ]


def update_author(
    conn: sqlite3.Connection,
    author_id: int,
    *,
    name: str | None = None,
    email: str | None = None,
) -> Author:
    """Patch an author; only supplied fields change.

    Args:
        conn: Open connection.
        author_id: Primary key to patch.
        name: New name, or None to keep.
        email: New email, or None to keep.

    Raises:
        NotFoundError: If the author is missing.
        ValueError: If a supplied field is blank.
        ConflictError: If the email is taken.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    if get_author(conn, author_id) is None:
        raise NotFoundError(f"author {author_id} not found")
    if name is not None and not name:
        raise ValueError("name must not be empty")
    if email is not None and not email:
        raise ValueError("email must not be empty")

    try:
        if name is not None:
            conn.execute("UPDATE authors SET name = ? WHERE id = ?", (name, author_id))
        if email is not None:
            conn.execute(
                "UPDATE authors SET email = ? WHERE id = ?", (email, author_id)
            )
    except sqlite3.IntegrityError as exc:
        raise ConflictError(f"email {email!r} is already taken") from exc
    conn.commit()

    updated = get_author(conn, author_id)
    if updated is None:
        raise LibraryError("author update succeeded but read-back failed")

    return updated


def delete_author(conn: sqlite3.Connection, author_id: int) -> None:
    """Delete an author; books, profile, and links cascade away.

    Args:
        conn: Open connection.
        author_id: Primary key to delete.

    Raises:
        NotFoundError: If the author is missing.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    cur = conn.execute("DELETE FROM authors WHERE id = ?", (author_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise NotFoundError(f"author {author_id} not found")


def upsert_profile(conn: sqlite3.Connection, author_id: int, bio: str) -> AuthorProfile:
    """Create or replace the 1:1 profile of an author in one statement.

    Args:
        conn: Open connection.
        author_id: Owner; must exist (UNIQUE keeps the 1:1 shape).
        bio: Profile text (must not be empty).

    Raises:
        NotFoundError: If the author is missing.
        ValueError: If the bio is empty.
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if get_author(conn, author_id) is None:
        raise NotFoundError(f"author {author_id} not found")
    if not bio:
        raise ValueError("bio must not be empty")

    conn.execute(
        "INSERT INTO author_profiles (author_id, bio) VALUES (?, ?) "
        "ON CONFLICT (author_id) DO UPDATE SET bio = excluded.bio",
        (author_id, bio),
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM author_profiles WHERE author_id = ?", (author_id,)
    ).fetchone()
    if row is None:
        raise LibraryError("profile upsert succeeded but read-back failed")

    return AuthorProfile.from_row(row)


def get_profile(conn: sqlite3.Connection, author_id: int) -> AuthorProfile | None:
    """Return the 1:1 profile of an author, else None (optional side).

    Args:
        conn: Open connection.
        author_id: Owner to look up.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    row = conn.execute(
        "SELECT * FROM author_profiles WHERE author_id = ?", (author_id,)
    ).fetchone()

    return AuthorProfile.from_row(row) if row else None


def create_book(
    conn: sqlite3.Connection,
    title: str,
    year: int,
    author_id: int,
    genre_ids: tuple[int, ...] = (),
) -> Book:
    """Insert one book plus its m:m genre links, returning the snapshot.

    Args:
        conn: Open connection.
        title: Book title (must not be empty).
        year: Publication year (must be positive).
        author_id: Owner; must exist (else the FK would reject it).
        genre_ids: Genre keys to link (each must exist).

    Raises:
        ValueError: On blank title or bad year.
        NotFoundError: On missing author or genre.
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if not title:
        raise ValueError("title must not be empty")
    if year <= 0:
        raise ValueError("year must be positive")
    if get_author(conn, author_id) is None:
        raise NotFoundError(f"author {author_id} not found")

    existing = {row["id"] for row in conn.execute("SELECT id FROM genres").fetchall()}
    missing = [g for g in genre_ids if g not in existing]
    if missing:
        raise NotFoundError(f"genres not found: {missing}")

    try:
        cur = conn.execute(
            "INSERT INTO books (title, year, author_id) VALUES (?, ?, ?)",
            (title, year, author_id),
        )
        conn.executemany(
            "INSERT OR IGNORE INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [(cur.lastrowid, g) for g in genre_ids],
        )
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise LibraryError("book insert failed integrity checks") from exc
    conn.commit()

    assert cur.lastrowid is not None
    book = get_book(conn, cur.lastrowid)
    if book is None:
        raise LibraryError("book insert succeeded but read-back failed")

    return book


def create_books_bulk(
    conn: sqlite3.Connection, rows: list[tuple[str, int, int]]
) -> list[Book]:
    """Insert many books in one round trip: validate once, write once.

    Args:
        conn: Open connection.
        rows: (title, year, author_id) triples. Must not be empty.

    Returns:
        Inserted books in input order.

    Raises:
        ValueError: On empty rows, blank titles, or bad years.
        NotFoundError: On a missing author (nothing is written).
        LibraryError: If the batch write itself fails (rolled back).
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if not rows:
        raise ValueError("rows must not be empty")
    if any(not title or year <= 0 for title, year, _ in rows):
        raise ValueError("every row needs a title and a positive year")

    wanted = {author_id for _, _, author_id in rows}
    slots = ",".join("?" * len(wanted))
    found = {
        row["id"]
        for row in conn.execute(
            f"SELECT id FROM authors WHERE id IN ({slots})", sorted(wanted)
        )
    }
    if wanted - found:
        raise NotFoundError(f"authors not found: {sorted(wanted - found)}")

    try:
        conn.executemany(
            "INSERT INTO books (title, year, author_id) VALUES (?, ?, ?)", rows
        )
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise LibraryError("bulk books insert failed; rolled back") from exc
    conn.commit()

    # Read back newest-first, then restore input order via rowids.
    fresh = conn.execute(
        "SELECT * FROM books ORDER BY id DESC LIMIT ?", (len(rows),)
    ).fetchall()

    return [Book.from_row(row) for row in reversed(fresh)]


def get_book(conn: sqlite3.Connection, book_id: int) -> Book | None:
    """Return one book by id, else None (no exception for absence).

    Args:
        conn: Open connection.
        book_id: Primary key to look up.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()

    return Book.from_row(row) if row else None


def list_books(
    conn: sqlite3.Connection,
    *,
    author_id: int | None = None,
    year: int | None = None,
    genre_id: int | None = None,
    query: str | None = None,
) -> list[Book]:
    """List books with optional filters, each hitting a real index.

    Args:
        conn: Open connection.
        author_id: Keep only this author's books (idx_books_author).
        year: Keep only this year (idx_books_year).
        genre_id: Keep books tagged so (idx_book_genres_genre).
        query: Case-insensitive title substring (LIKE, escaped).

    Returns:
        Matching books ordered by id.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    # Genre filter needs the junction table; the rest filter books alone.
    if genre_id is not None:
        sql = (
            "SELECT b.* FROM books b "
            "JOIN book_genres g ON g.book_id = b.id "
            "WHERE g.genre_id = ?"
        )
        args: list[object] = [genre_id]
    else:
        sql = "SELECT b.* FROM books b WHERE 1 = 1"
        args = []

    if author_id is not None:
        sql += " AND b.author_id = ?"
        args.append(author_id)
    if year is not None:
        sql += " AND b.year = ?"
        args.append(year)
    if query:
        sql += " AND b.title LIKE ? ESCAPE '\\'"
        args.append(f"%{_like_escape(query)}%")
    sql += " ORDER BY b.id"

    return [Book.from_row(row) for row in conn.execute(sql, args)]


def get_book_detail(conn: sqlite3.Connection, book_id: int) -> BookDetail | None:
    """Return a book with author name and genre names (one joined read).

    Args:
        conn: Open connection.
        book_id: Primary key to expand.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    book = get_book(conn, book_id)
    if book is None:
        return None

    author = get_author(conn, book.author_id)
    genres = [
        row["name"]
        for row in conn.execute(
            "SELECT g.name FROM genres g "
            "JOIN book_genres j ON j.genre_id = g.id "
            "WHERE j.book_id = ? ORDER BY g.name",
            (book_id,),
        )
    ]

    return BookDetail(
        book=book,
        author_name=author.name if author else "?",
        genres=tuple(genres),
    )


def update_book(
    conn: sqlite3.Connection,
    book_id: int,
    *,
    title: str | None = None,
    year: int | None = None,
    author_id: int | None = None,
) -> Book:
    """Patch a book; only supplied fields change.

    Args:
        conn: Open connection.
        book_id: Primary key to patch.
        title: New title, or None to keep.
        year: New year, or None to keep.
        author_id: New owner, or None to keep (must exist).

    Raises:
        NotFoundError: If the book or new author is missing.
        ValueError: If a supplied field is blank or bad.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    if get_book(conn, book_id) is None:
        raise NotFoundError(f"book {book_id} not found")
    if title is not None and not title:
        raise ValueError("title must not be empty")
    if year is not None and year <= 0:
        raise ValueError("year must be positive")
    if author_id is not None and get_author(conn, author_id) is None:
        raise NotFoundError(f"author {author_id} not found")

    if title is not None:
        conn.execute("UPDATE books SET title = ? WHERE id = ?", (title, book_id))
    if year is not None:
        conn.execute("UPDATE books SET year = ? WHERE id = ?", (year, book_id))
    if author_id is not None:
        conn.execute(
            "UPDATE books SET author_id = ? WHERE id = ?", (author_id, book_id)
        )
    conn.commit()

    updated = get_book(conn, book_id)
    if updated is None:
        raise LibraryError("book update succeeded but read-back failed")

    return updated


def delete_book(conn: sqlite3.Connection, book_id: int) -> None:
    """Delete one book; its junction links cascade away.

    Args:
        conn: Open connection.
        book_id: Primary key to delete.

    Raises:
        NotFoundError: If the book is missing.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    cur = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise NotFoundError(f"book {book_id} not found")


def delete_books_bulk(conn: sqlite3.Connection, ids: list[int]) -> int:
    """Delete many books in one statement, returning the deleted count.

    Args:
        conn: Open connection.
        ids: Primary keys to delete. Empty deletes nothing.

    Returns:
        How many rows actually vanished (junction links cascade).
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if not ids:
        return 0

    slots = ",".join("?" * len(ids))
    cur = conn.execute(f"DELETE FROM books WHERE id IN ({slots})", ids)
    conn.commit()

    return cur.rowcount


def create_genre(conn: sqlite3.Connection, name: str) -> Genre:
    """Insert one genre, returning the stored snapshot.

    Args:
        conn: Open connection.
        name: Unique genre name (must not be empty).

    Raises:
        ValueError: If the name is empty.
        ConflictError: If the name is taken.
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if not name:
        raise ValueError("name must not be empty")

    try:
        cur = conn.execute("INSERT INTO genres (name) VALUES (?)", (name,))
    except sqlite3.IntegrityError as exc:
        raise ConflictError(f"genre {name!r} is already taken") from exc
    conn.commit()

    row = conn.execute("SELECT * FROM genres WHERE id = ?", (cur.lastrowid,)).fetchone()
    if row is None:
        raise LibraryError("genre insert succeeded but read-back failed")

    return Genre.from_row(row)


def list_genres(conn: sqlite3.Connection) -> list[Genre]:
    """Return every genre ordered by name (stable listing).

    Args:
        conn: Open connection.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    return [
        Genre.from_row(row)
        for row in conn.execute("SELECT * FROM genres ORDER BY name")
    ]


def add_genre_to_book(conn: sqlite3.Connection, book_id: int, genre_id: int) -> None:
    """Tag a book (m:m link); re-tagging the same pair is a no-op.

    Args:
        conn: Open connection.
        book_id: Book side; must exist.
        genre_id: Genre side; must exist.

    Raises:
        NotFoundError: If either side is missing.
    """
    if conn is None:
        raise ValueError("conn must not be None")
    if get_book(conn, book_id) is None:
        raise NotFoundError(f"book {book_id} not found")

    cur = conn.execute(
        "INSERT OR IGNORE INTO book_genres (book_id, genre_id) VALUES (?, ?)",
        (book_id, genre_id),
    )
    # OR IGNORE hides NOTHING here: zero rows means the genre is missing.
    if cur.rowcount == 0:
        still = conn.execute(
            "SELECT 1 FROM genres WHERE id = ?", (genre_id,)
        ).fetchone()
        if still is None:
            raise NotFoundError(f"genre {genre_id} not found")
    conn.commit()


def remove_genre_from_book(
    conn: sqlite3.Connection, book_id: int, genre_id: int
) -> None:
    """Untag a book; removing a missing tag is a silent no-op.

    Args:
        conn: Open connection.
        book_id: Book side of the link.
        genre_id: Genre side of the link.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    conn.execute(
        "DELETE FROM book_genres WHERE book_id = ? AND genre_id = ?",
        (book_id, genre_id),
    )
    conn.commit()


def get_author_detail(conn: sqlite3.Connection, author_id: int) -> AuthorDetail | None:
    """Return an author with optional bio and books (LEFT JOIN inside).

    Args:
        conn: Open connection.
        author_id: Primary key to expand.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    author = get_author(conn, author_id)
    if author is None:
        return None

    profile = get_profile(conn, author_id)
    books = [
        Book.from_row(row)
        for row in conn.execute(
            "SELECT * FROM books WHERE author_id = ? ORDER BY id", (author_id,)
        )
    ]

    return AuthorDetail(
        author=author, bio=profile.bio if profile else None, books=tuple(books)
    )


def count_books_per_author(conn: sqlite3.Connection) -> dict[str, int]:
    """Return author name to book count (one GROUP BY, feeds stats).

    Args:
        conn: Open connection.
    """
    if conn is None:
        raise ValueError("conn must not be None")

    return {
        row["name"]: row["n"]
        for row in conn.execute(
            "SELECT a.name AS name, COUNT(b.id) AS n FROM authors a "
            "LEFT JOIN books b ON b.author_id = a.id "
            "GROUP BY a.id ORDER BY a.name"
        )
    }
