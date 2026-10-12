"""Typed record shapes for the library domain (pure data, no I/O)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Author:
    """An author row. Immutable snapshot, never a live handle."""

    id: int
    name: str
    email: str
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Author:
        """Build from a DB row (named constructor; cls keeps subclasses)."""
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            created_at=row["created_at"],
        )


@dataclass(frozen=True)
class AuthorProfile:
    """The 1:1 sidecar of an author row (bio lives apart, not inline)."""

    id: int
    author_id: int
    bio: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> AuthorProfile:
        """Build from a DB row (named constructor; cls keeps subclasses)."""
        return cls(id=row["id"], author_id=row["author_id"], bio=row["bio"])


@dataclass(frozen=True)
class Book:
    """A book row. The many side of the author 1:many link."""

    id: int
    title: str
    year: int
    author_id: int

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Book:
        """Build from a DB row (named constructor; cls keeps subclasses)."""
        return cls(
            id=row["id"],
            title=row["title"],
            year=row["year"],
            author_id=row["author_id"],
        )


@dataclass(frozen=True)
class Genre:
    """A genre row. One side of the book m:m link."""

    id: int
    name: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Genre:
        """Build from a DB row (named constructor; cls keeps subclasses)."""
        return cls(id=row["id"], name=row["name"])


@dataclass(frozen=True)
class BookDetail:
    """A book plus its author name and genre names (one joined read)."""

    book: Book
    author_name: str
    genres: tuple[str, ...]


@dataclass(frozen=True)
class AuthorDetail:
    """An author plus optional bio and their books (one joined read)."""

    author: Author
    bio: str | None
    books: tuple[Book, ...]

    @property
    def book_count(self) -> int:
        """Return how many books are held (cheap derived read)."""
        return len(self.books)
