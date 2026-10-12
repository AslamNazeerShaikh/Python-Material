"""Application service: the DIP seam between HTTP routes and SQL.

SOLID placement: routes depend on the small role Protocols below
(ISP), never on concrete repository functions (DIP). This class owns
orchestration only — multi-step flows, stats, recent-query memory —
and zero SQL text (SRP). Anything implementing the Protocols (fakes
in tests, this class in prod) substitutes freely (LSP).
"""

from __future__ import annotations

import sqlite3
from collections import Counter, deque
from typing import Protocol, runtime_checkable

from python_material.library import repository
from python_material.library.errors import LibraryError
from python_material.library.models import (
    Author,
    AuthorDetail,
    AuthorProfile,
    Book,
    BookDetail,
    Genre,
)


@runtime_checkable
class CatalogReader(Protocol):
    """Read role: listings, lookups, details, search, stats."""

    def list_authors(self) -> list[Author]: ...
    def get_author_detail(self, author_id: int) -> AuthorDetail | None: ...
    def list_books(
        self,
        *,
        author_id: int | None = ...,
        year: int | None = ...,
        genre_id: int | None = ...,
        query: str | None = ...,
    ) -> list[Book]: ...
    def get_book_detail(self, book_id: int) -> BookDetail | None: ...
    def list_genres(self) -> list[Genre]: ...
    def books_per_author(self) -> list[tuple[str, int]]: ...


@runtime_checkable
class CatalogWriter(Protocol):
    """Write role: creates, patches, deletes, links."""

    def create_author(self, name: str, email: str) -> Author: ...
    def create_authors_bulk(self, rows: list[tuple[str, str]]) -> list[Author]: ...
    def update_author(
        self, author_id: int, *, name: str | None = ..., email: str | None = ...
    ) -> Author: ...
    def delete_author(self, author_id: int) -> None: ...
    def upsert_profile(self, author_id: int, bio: str) -> AuthorProfile: ...
    def create_book(
        self,
        title: str,
        year: int,
        author_id: int,
        genre_ids: tuple[int, ...] = ...,
    ) -> Book: ...
    def create_books_bulk(self, rows: list[tuple[str, int, int]]) -> list[Book]: ...
    def update_book(
        self,
        book_id: int,
        *,
        title: str | None = ...,
        year: int | None = ...,
        author_id: int | None = ...,
    ) -> Book: ...
    def delete_book(self, book_id: int) -> None: ...
    def delete_books_bulk(self, ids: list[int]) -> int: ...
    def create_genre(self, name: str) -> Genre: ...
    def add_genre_to_book(self, book_id: int, genre_id: int) -> None: ...
    def remove_genre_from_book(self, book_id: int, genre_id: int) -> None: ...
    def register_author_with_books(
        self, name: str, email: str, books: list[tuple[str, int]]
    ) -> AuthorDetail: ...


class LibraryService:
    """Orchestrates repository calls for one connection (DIP target).

    The connection is INJECTED, never opened here: high-level policy
    stays independent of connection plumbing (DIP). State is private
    (`self._conn`, `self._recent`); callers use methods only (11).
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Bind to an open connection plus a bounded recent-query log."""
        if conn is None:
            raise ValueError("conn must not be None")
        self._conn = conn
        self._recent: deque[str] = deque(maxlen=10)

    @property
    def recent_queries(self) -> tuple[str, ...]:
        """Return an immutable snapshot of recent searches (newest last)."""
        return tuple(self._recent)

    def list_authors(self) -> list[Author]:
        """Return every author ordered by id (read role)."""
        return repository.list_authors(self._conn)

    def get_author_detail(self, author_id: int) -> AuthorDetail | None:
        """Return an author with bio and books, else None (read role)."""
        return repository.get_author_detail(self._conn, author_id)

    def list_books(
        self,
        *,
        author_id: int | None = None,
        year: int | None = None,
        genre_id: int | None = None,
        query: str | None = None,
    ) -> list[Book]:
        """List filtered books, remembering text searches (read role)."""
        if query:
            self._recent.append(query)
        return repository.list_books(
            self._conn,
            author_id=author_id,
            year=year,
            genre_id=genre_id,
            query=query,
        )

    def get_book_detail(self, book_id: int) -> BookDetail | None:
        """Return a book with author and genres, else None (read role)."""
        return repository.get_book_detail(self._conn, book_id)

    def list_genres(self) -> list[Genre]:
        """Return every genre ordered by name (read role)."""
        return repository.list_genres(self._conn)

    def books_per_author(self) -> list[tuple[str, int]]:
        """Rank authors by book count via Counter (read role, 13 demo)."""
        counts: Counter[str] = Counter(repository.count_books_per_author(self._conn))

        return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))

    def create_author(self, name: str, email: str) -> Author:
        """Create one author (write role, conflicts surface typed)."""
        return repository.create_author(self._conn, name, email)

    def create_authors_bulk(self, rows: list[tuple[str, str]]) -> list[Author]:
        """Create many authors atomically (write role)."""
        return repository.create_authors_bulk(self._conn, rows)

    def update_author(
        self, author_id: int, *, name: str | None = None, email: str | None = None
    ) -> Author:
        """Patch an author; supplied fields only (write role)."""
        return repository.update_author(self._conn, author_id, name=name, email=email)

    def delete_author(self, author_id: int) -> None:
        """Delete an author with cascade (write role)."""
        repository.delete_author(self._conn, author_id)

    def upsert_profile(self, author_id: int, bio: str) -> AuthorProfile:
        """Create or replace the 1:1 profile (write role)."""
        return repository.upsert_profile(self._conn, author_id, bio)

    def create_book(
        self,
        title: str,
        year: int,
        author_id: int,
        genre_ids: tuple[int, ...] = (),
    ) -> Book:
        """Create one book plus genre links (write role)."""
        return repository.create_book(self._conn, title, year, author_id, genre_ids)

    def create_books_bulk(self, rows: list[tuple[str, int, int]]) -> list[Book]:
        """Create many books atomically (write role)."""
        return repository.create_books_bulk(self._conn, rows)

    def update_book(
        self,
        book_id: int,
        *,
        title: str | None = None,
        year: int | None = None,
        author_id: int | None = None,
    ) -> Book:
        """Patch a book; supplied fields only (write role)."""
        return repository.update_book(
            self._conn, book_id, title=title, year=year, author_id=author_id
        )

    def delete_book(self, book_id: int) -> None:
        """Delete one book with cascade (write role)."""
        repository.delete_book(self._conn, book_id)

    def delete_books_bulk(self, ids: list[int]) -> int:
        """Delete many books in one statement (write role)."""
        return repository.delete_books_bulk(self._conn, ids)

    def create_genre(self, name: str) -> Genre:
        """Create one genre (write role)."""
        return repository.create_genre(self._conn, name)

    def add_genre_to_book(self, book_id: int, genre_id: int) -> None:
        """Tag a book; re-tagging is a no-op (write role)."""
        repository.add_genre_to_book(self._conn, book_id, genre_id)

    def remove_genre_from_book(self, book_id: int, genre_id: int) -> None:
        """Untag a book; missing links delete silently (write role)."""
        repository.remove_genre_from_book(self._conn, book_id, genre_id)

    def register_author_with_books(
        self, name: str, email: str, books: list[tuple[str, int]]
    ) -> AuthorDetail:
        """Register an author plus their first books as one guarded flow.

        Validate-first, then write; if the book batch fails after the
        author row lands, the author is removed again (compensation:
        no orphan author survives a failed registration).

        Args:
            name: Author display name.
            email: Unique contact address.
            books: (title, year) pairs to create for the author.

        Raises:
            ValueError: On blank fields or bad years.
            LibraryError: If books fail after compensation details attach.
        """
        if not name:
            raise ValueError("name must not be empty")
        if not email:
            raise ValueError("email must not be empty")
        if any(not title or year <= 0 for title, year in books):
            raise ValueError("every book needs a title and a positive year")

        author = repository.create_author(self._conn, name, email)
        try:
            repository.create_books_bulk(
                self._conn, [(title, year, author.id) for title, year in books]
            )
        except ValueError as exc:
            repository.delete_author(self._conn, author.id)
            raise LibraryError(f"registration compensated: {exc}") from exc

        detail = repository.get_author_detail(self._conn, author.id)
        if detail is None:
            raise LibraryError("registration succeeded but read-back failed")

        return detail
