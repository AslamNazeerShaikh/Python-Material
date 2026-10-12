# ruff: noqa: B008 - Depends() in defaults is the documented FastAPI pattern.
"""FastAPI over the library service: JSON CRUD plus Scalar docs.

Two launches (same app object either way):

- Menu: ``python3 demos/main.py`` option 1 (server + browser, Enter stops).
- Standalone: ``python3 -m python_material.library.api`` from any terminal
  (or ``python3 -m uvicorn python_material.library.api:app --reload``).

SOLID placement: routes are thin translators only (SRP) — they shape
wire models and map domain errors to HTTP. All policy lives in
LibraryService behind the CatalogReader/CatalogWriter Protocols, which
routes receive via Depends injection (DIP/ISP). Response schemas
inherit request shapes (LSP), and new endpoints extend without touching
old ones (OCP).

This module needs FastAPI at RUNTIME only; importing it without the
api extra raises ImportError at the fastapi import below (by design:
servers are not library code). Repository tests never touch this file.
"""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from python_material.library import database
from python_material.library.errors import ConflictError, NotFoundError
from python_material.library.models import Book
from python_material.library.service import (
    CatalogReader,
    CatalogWriter,
    LibraryService,
)


class AuthorIn(BaseModel):
    """Author write shape: everything the client supplies."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)


class AuthorOut(BaseModel):
    """Author read shape: stored snapshot including id and timestamp."""

    id: int
    name: str
    email: str
    created_at: str


class AuthorPatch(BaseModel):
    """Author partial update: every field optional, at least one lands."""

    name: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=3)


class ProfileIn(BaseModel):
    """Profile write shape: the 1:1 bio text."""

    bio: str = Field(min_length=1)


class ProfileOut(BaseModel):
    """Profile read shape: stored snapshot with owner link."""

    id: int
    author_id: int
    bio: str


class BookIn(BaseModel):
    """Book write shape: scalar fields plus m:m genre links."""

    title: str = Field(min_length=1)
    year: int = Field(gt=0)
    author_id: int = Field(gt=0)
    genre_ids: list[int] = Field(default_factory=list)


class BookOut(BaseModel):
    """Book read shape: stored snapshot (genres via the detail route)."""

    id: int
    title: str
    year: int
    author_id: int


class BookPatch(BaseModel):
    """Book partial update: every field optional."""

    title: str | None = Field(default=None, min_length=1)
    year: int | None = Field(default=None, gt=0)
    author_id: int | None = Field(default=None, gt=0)


class BookDetailOut(BookOut):
    """Book read shape expanded with author name and genre names (LSP)."""

    author_name: str
    genres: list[str]


class AuthorDetailOut(AuthorOut):
    """Author read shape expanded with bio, books, and count (LSP)."""

    bio: str | None
    books: list[BookOut]
    book_count: int


class GenreIn(BaseModel):
    """Genre write shape: the unique name."""

    name: str = Field(min_length=1)


class GenreOut(BaseModel):
    """Genre read shape: stored snapshot."""

    id: int
    name: str


class BulkDeleteIn(BaseModel):
    """Bulk delete shape: ids to remove, count returned."""

    ids: list[int] = Field(min_length=1)


class BookSeedIn(BaseModel):
    """One book inside a registration batch (title + year only)."""

    title: str = Field(min_length=1)
    year: int = Field(gt=0)


class AuthorWithBooksIn(BaseModel):
    """Registration shape: author plus their first books (OCP story)."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    books: list[BookSeedIn] = Field(default_factory=list)


class AuthorStatsOut(BaseModel):
    """Stats row: author name with their book count, ranked."""

    author: str
    books: int


def _book_out(book: Book) -> BookOut:
    """Shape a Book dataclass into its wire form (one shaping point)."""
    return BookOut(
        id=book.id, title=book.title, year=book.year, author_id=book.author_id
    )


def _http_error(exc: ValueError) -> HTTPException:
    """Map one domain error to its HTTP twin (single mapping point)."""
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=409, detail=str(exc))

    return HTTPException(status_code=400, detail=str(exc))


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield one connection per request, always closed afterwards."""
    conn = database.connect()
    try:
        yield conn
    finally:
        conn.close()


def get_service(
    conn: sqlite3.Connection = Depends(get_db),
) -> LibraryService:
    """Inject the concrete service (DIP provider; routes see Protocols)."""
    return LibraryService(conn)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Boot hook: create schema and seed demo data when empty."""
    conn = database.connect()
    try:
        database.init_db(conn)
        database.seed(conn)
    finally:
        conn.close()
    yield


app = FastAPI(title="Library CRUD API", lifespan=lifespan)


def _scalar_missing() -> dict[str, str]:
    """Explain the missing optional dependency instead of 404ing."""
    raise HTTPException(
        status_code=501,
        detail="Scalar UI needs: python3 -m pip install scalar-fastapi",
    )


def _mount_scalar_docs() -> None:
    """Serve Scalar UI at /scalar, or an explicit 501 without the extra."""
    try:
        from scalar_fastapi import add_scalar_reference
    except ImportError:
        app.get("/scalar", include_in_schema=False)(_scalar_missing)

        return

    add_scalar_reference(app)


_mount_scalar_docs()


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe for uptime checks and smoke tests."""
    return {"status": "ok"}


@app.post("/authors", response_model=AuthorOut, status_code=201)
def create_author(
    payload: AuthorIn, service: CatalogWriter = Depends(get_service)
) -> AuthorOut:
    """Create a single author (409 on taken email)."""
    try:
        author = service.create_author(payload.name, payload.email)
    except ValueError as exc:
        raise _http_error(exc) from exc

    return AuthorOut(**author.__dict__)


@app.post("/authors/bulk", response_model=list[AuthorOut], status_code=201)
def create_authors_bulk(
    payload: list[AuthorIn], service: CatalogWriter = Depends(get_service)
) -> list[AuthorOut]:
    """Create many authors atomically (all-or-nothing on taken email)."""
    try:
        authors = service.create_authors_bulk([(a.name, a.email) for a in payload])
    except ValueError as exc:
        raise _http_error(exc) from exc

    return [AuthorOut(**a.__dict__) for a in authors]


@app.post("/authors/with-books", response_model=AuthorDetailOut, status_code=201)
def register_author_with_books(
    payload: AuthorWithBooksIn, service: CatalogWriter = Depends(get_service)
) -> AuthorDetailOut:
    """Register an author plus first books as one guarded flow (OCP new)."""
    try:
        detail = service.register_author_with_books(
            payload.name,
            payload.email,
            [(b.title, b.year) for b in payload.books],
        )
    except ValueError as exc:
        raise _http_error(exc) from exc

    return AuthorDetailOut(
        **detail.author.__dict__,
        bio=detail.bio,
        books=[_book_out(b) for b in detail.books],
        book_count=detail.book_count,
    )


@app.get("/authors", response_model=list[AuthorOut])
def list_authors(service: CatalogReader = Depends(get_service)) -> list[AuthorOut]:
    """List every author ordered by id."""
    return [AuthorOut(**a.__dict__) for a in service.list_authors()]


@app.get("/authors/{author_id}", response_model=AuthorDetailOut)
def get_author_detail(
    author_id: int, service: CatalogReader = Depends(get_service)
) -> AuthorDetailOut:
    """Read an author with optional bio and owned books (404 when missing)."""
    detail = service.get_author_detail(author_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="author not found")

    return AuthorDetailOut(
        **detail.author.__dict__,
        bio=detail.bio,
        books=[_book_out(b) for b in detail.books],
        book_count=detail.book_count,
    )


@app.patch("/authors/{author_id}", response_model=AuthorOut)
def update_author(
    author_id: int,
    payload: AuthorPatch,
    service: CatalogWriter = Depends(get_service),
) -> AuthorOut:
    """Patch an author; supplied fields only (400/409 on bad input)."""
    try:
        author = service.update_author(
            author_id, name=payload.name, email=payload.email
        )
    except ValueError as exc:
        raise _http_error(exc) from exc

    return AuthorOut(**author.__dict__)


@app.delete("/authors/{author_id}", status_code=204)
def delete_author(
    author_id: int, service: CatalogWriter = Depends(get_service)
) -> None:
    """Delete an author; books, profile, and links cascade (404 missing)."""
    try:
        service.delete_author(author_id)
    except ValueError as exc:
        raise _http_error(exc) from exc


@app.put("/authors/{author_id}/profile", response_model=ProfileOut)
def upsert_profile(
    author_id: int,
    payload: ProfileIn,
    service: CatalogWriter = Depends(get_service),
) -> ProfileOut:
    """Create or replace the 1:1 profile (400 on missing author)."""
    try:
        profile = service.upsert_profile(author_id, payload.bio)
    except ValueError as exc:
        raise _http_error(exc) from exc

    return ProfileOut(**profile.__dict__)


@app.post("/books", response_model=BookOut, status_code=201)
def create_book(
    payload: BookIn, service: CatalogWriter = Depends(get_service)
) -> BookOut:
    """Create a single book plus genre links (400 on missing refs)."""
    try:
        book = service.create_book(
            payload.title, payload.year, payload.author_id, tuple(payload.genre_ids)
        )
    except ValueError as exc:
        raise _http_error(exc) from exc

    return _book_out(book)


@app.post("/books/bulk", response_model=list[BookOut], status_code=201)
def create_books_bulk(
    payload: list[BookIn], service: CatalogWriter = Depends(get_service)
) -> list[BookOut]:
    """Create many books atomically (rolls back on any missing author)."""
    try:
        books = service.create_books_bulk(
            [(b.title, b.year, b.author_id) for b in payload]
        )
    except ValueError as exc:
        raise _http_error(exc) from exc

    return [_book_out(b) for b in books]


@app.get("/books", response_model=list[BookOut])
def list_books(
    service: CatalogReader = Depends(get_service),
    author_id: int | None = Query(default=None, gt=0),
    year: int | None = Query(default=None, gt=0),
    genre_id: int | None = Query(default=None, gt=0),
    q: str | None = Query(default=None, min_length=1),
) -> list[BookOut]:
    """List books with optional author/year/genre/title filters combined."""
    books = service.list_books(
        author_id=author_id, year=year, genre_id=genre_id, query=q
    )

    return [_book_out(b) for b in books]


@app.get("/books/{book_id}", response_model=BookDetailOut)
def get_book_detail(
    book_id: int, service: CatalogReader = Depends(get_service)
) -> BookDetailOut:
    """Read a book with author name and genre names (404 when missing)."""
    detail = service.get_book_detail(book_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="book not found")

    return BookDetailOut(
        **_book_out(detail.book).model_dump(),
        author_name=detail.author_name,
        genres=list(detail.genres),
    )


@app.patch("/books/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    payload: BookPatch,
    service: CatalogWriter = Depends(get_service),
) -> BookOut:
    """Patch a book; supplied fields only (400 on missing refs)."""
    try:
        book = service.update_book(
            book_id,
            title=payload.title,
            year=payload.year,
            author_id=payload.author_id,
        )
    except ValueError as exc:
        raise _http_error(exc) from exc

    return _book_out(book)


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, service: CatalogWriter = Depends(get_service)) -> None:
    """Delete one book; junction links cascade (404 when missing)."""
    try:
        service.delete_book(book_id)
    except ValueError as exc:
        raise _http_error(exc) from exc


@app.post("/books/bulk-delete")
def delete_books_bulk(
    payload: BulkDeleteIn, service: CatalogWriter = Depends(get_service)
) -> dict[str, int]:
    """Delete many books in one statement; reports the deleted count."""
    deleted = service.delete_books_bulk(payload.ids)

    return {"deleted": deleted}


@app.post("/genres", response_model=GenreOut, status_code=201)
def create_genre(
    payload: GenreIn, service: CatalogWriter = Depends(get_service)
) -> GenreOut:
    """Create a single genre (409 on taken name)."""
    try:
        genre = service.create_genre(payload.name)
    except ValueError as exc:
        raise _http_error(exc) from exc

    return GenreOut(**genre.__dict__)


@app.get("/genres", response_model=list[GenreOut])
def list_genres(service: CatalogReader = Depends(get_service)) -> list[GenreOut]:
    """List every genre ordered by name."""
    return [GenreOut(**g.__dict__) for g in service.list_genres()]


@app.post("/books/{book_id}/genres/{genre_id}", status_code=204)
def tag_book(
    book_id: int,
    genre_id: int,
    service: CatalogWriter = Depends(get_service),
) -> None:
    """Link one m:m tag; re-tagging is a no-op (400 on missing refs)."""
    try:
        service.add_genre_to_book(book_id, genre_id)
    except ValueError as exc:
        raise _http_error(exc) from exc


@app.delete("/books/{book_id}/genres/{genre_id}", status_code=204)
def untag_book(
    book_id: int,
    genre_id: int,
    service: CatalogWriter = Depends(get_service),
) -> None:
    """Unlink one m:m tag; missing links delete silently."""
    service.remove_genre_from_book(book_id, genre_id)


@app.get("/genres/{genre_id}/books", response_model=list[BookOut])
def list_books_by_genre(
    genre_id: int, service: CatalogReader = Depends(get_service)
) -> list[BookOut]:
    """List every book carrying a genre (m:m read through the junction)."""
    books = service.list_books(genre_id=genre_id)

    return [_book_out(b) for b in books]


@app.get("/stats/books-per-author", response_model=list[AuthorStatsOut])
def books_per_author(
    service: CatalogReader = Depends(get_service),
) -> list[AuthorStatsOut]:
    """Rank authors by book count (Counter + lambda sort, 13 demo)."""
    return [
        AuthorStatsOut(author=name, books=count)
        for name, count in service.books_per_author()
    ]


if __name__ == "__main__":
    """Standalone launch: python3 -m python_material.library.api (any shell)."""
    try:
        import uvicorn
    except ImportError:
        raise SystemExit(
            "uvicorn missing: python3 -m pip install -e '.[api]'"
        ) from None

    uvicorn.run("python_material.library.api:app", host="127.0.0.1", port=8000)
