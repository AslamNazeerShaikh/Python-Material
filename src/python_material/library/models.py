"""Typed record shapes for the library domain (pure data, no I/O)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Author:
    """An author row. Immutable snapshot, never a live handle."""

    id: int
    name: str
    email: str
    created_at: str


@dataclass(frozen=True)
class AuthorProfile:
    """The 1:1 sidecar of an author row (bio lives apart, not inline)."""

    id: int
    author_id: int
    bio: str


@dataclass(frozen=True)
class Book:
    """A book row. The many side of the author 1:many link."""

    id: int
    title: str
    year: int
    author_id: int


@dataclass(frozen=True)
class Genre:
    """A genre row. One side of the book m:m link."""

    id: int
    name: str


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
