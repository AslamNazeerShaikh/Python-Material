# ruff: noqa: B008 - Depends() in defaults is the documented FastAPI pattern.
"""FastAPI over the library repository: JSON CRUD plus Scalar docs.

Run (from the repo root, after installing the api extra)::

    python3 -m pip install -e ".[api]"
    python3 -m uvicorn python_material.library.api:app --reload

Then open http://127.0.0.1:8000/scalar (Scalar UI), /docs (Swagger),
or /openapi.json (raw schema). The database seeds itself on startup
when empty, so the first boot already serves demo data.

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

from python_material.library import database, repository
from python_material.library.models import Book


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
    """Book read shape expanded with author name and genre names."""

    author_name: str
    genres: list[str]


class AuthorDetailOut(AuthorOut):
    """Author read shape expanded with optional bio and owned books."""

    bio: str | None
    books: list[BookOut]


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


def _book_out(book: Book) -> BookOut:
    """Shape a Book dataclass into its wire form (one shaping point)."""
    return BookOut(
        id=book.id, title=book.title, year=book.year, author_id=book.author_id
    )


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield one connection per request, always closed afterwards."""
    conn = database.connect()
    try:
        yield conn
    finally:
        conn.close()


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


def _mount_scalar_docs() -> None:
    """Serve Scalar UI at /scalar, or an explicit 501 without the extra."""
    try:
        from scalar_fastapi import add_scalar_reference
    except ImportError:

        @app.get("/scalar", include_in_schema=False)
        def scalar_missing() -> dict[str, str]:
            """Explain the missing optional dependency instead of 404ing."""
            raise HTTPException(
                status_code=501,
                detail="Scalar UI needs: python3 -m pip install scalar-fastapi",
            )

        return

    add_scalar_reference(app)


_mount_scalar_docs()


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe for uptime checks and smoke tests."""
    return {"status": "ok"}


@app.post("/authors", response_model=AuthorOut, status_code=201)
def create_author(
    payload: AuthorIn, conn: sqlite3.Connection = Depends(get_db)
) -> AuthorOut:
    """Create a single author (409 on taken email)."""
    try:
        author = repository.create_author(conn, payload.name, payload.email)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return AuthorOut(**author.__dict__)


@app.post("/authors/bulk", response_model=list[AuthorOut], status_code=201)
def create_authors_bulk(
    payload: list[AuthorIn], conn: sqlite3.Connection = Depends(get_db)
) -> list[AuthorOut]:
    """Create many authors atomically (all-or-nothing on taken email)."""
    try:
        authors = repository.create_authors_bulk(
            conn, [(a.name, a.email) for a in payload]
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return [AuthorOut(**a.__dict__) for a in authors]


@app.get("/authors", response_model=list[AuthorOut])
def list_authors(conn: sqlite3.Connection = Depends(get_db)) -> list[AuthorOut]:
    """List every author ordered by id."""
    return [AuthorOut(**a.__dict__) for a in repository.list_authors(conn)]


@app.get("/authors/{author_id}", response_model=AuthorDetailOut)
def get_author_detail(
    author_id: int, conn: sqlite3.Connection = Depends(get_db)
) -> AuthorDetailOut:
    """Read an author with optional bio and owned books (404 when missing)."""
    detail = repository.get_author_detail(conn, author_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="author not found")

    return AuthorDetailOut(
        **detail.author.__dict__,
        bio=detail.bio,
        books=[_book_out(b) for b in detail.books],
    )


@app.patch("/authors/{author_id}", response_model=AuthorOut)
def update_author(
    author_id: int,
    payload: AuthorPatch,
    conn: sqlite3.Connection = Depends(get_db),
) -> AuthorOut:
    """Patch an author; supplied fields only (400 on missing/taken)."""
    try:
        author = repository.update_author(
            conn, author_id, name=payload.name, email=payload.email
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AuthorOut(**author.__dict__)


@app.delete("/authors/{author_id}", status_code=204)
def delete_author(author_id: int, conn: sqlite3.Connection = Depends(get_db)) -> None:
    """Delete an author; books, profile, and links cascade (404 missing)."""
    try:
        repository.delete_author(conn, author_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/authors/{author_id}/profile", response_model=ProfileOut)
def upsert_profile(
    author_id: int,
    payload: ProfileIn,
    conn: sqlite3.Connection = Depends(get_db),
) -> ProfileOut:
    """Create or replace the 1:1 profile (400 on missing author)."""
    try:
        profile = repository.upsert_profile(conn, author_id, payload.bio)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ProfileOut(**profile.__dict__)


@app.post("/books", response_model=BookOut, status_code=201)
def create_book(payload: BookIn, conn: sqlite3.Connection = Depends(get_db)) -> BookOut:
    """Create a single book plus genre links (400 on missing refs)."""
    try:
        book = repository.create_book(
            conn,
            payload.title,
            payload.year,
            payload.author_id,
            tuple(payload.genre_ids),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _book_out(book)


@app.post("/books/bulk", response_model=list[BookOut], status_code=201)
def create_books_bulk(
    payload: list[BookIn], conn: sqlite3.Connection = Depends(get_db)
) -> list[BookOut]:
    """Create many books atomically (rolls back on any missing author)."""
    try:
        books = repository.create_books_bulk(
            conn, [(b.title, b.year, b.author_id) for b in payload]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [_book_out(b) for b in books]


@app.get("/books", response_model=list[BookOut])
def list_books(
    conn: sqlite3.Connection = Depends(get_db),
    author_id: int | None = Query(default=None, gt=0),
    year: int | None = Query(default=None, gt=0),
    genre_id: int | None = Query(default=None, gt=0),
    q: str | None = Query(default=None, min_length=1),
) -> list[BookOut]:
    """List books with optional author/year/genre/title filters combined."""
    books = repository.list_books(
        conn, author_id=author_id, year=year, genre_id=genre_id, query=q
    )

    return [_book_out(b) for b in books]


@app.get("/books/{book_id}", response_model=BookDetailOut)
def get_book_detail(
    book_id: int, conn: sqlite3.Connection = Depends(get_db)
) -> BookDetailOut:
    """Read a book with author name and genre names (404 when missing)."""
    detail = repository.get_book_detail(conn, book_id)
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
    conn: sqlite3.Connection = Depends(get_db),
) -> BookOut:
    """Patch a book; supplied fields only (400 on missing refs)."""
    try:
        book = repository.update_book(
            conn,
            book_id,
            title=payload.title,
            year=payload.year,
            author_id=payload.author_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _book_out(book)


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, conn: sqlite3.Connection = Depends(get_db)) -> None:
    """Delete one book; junction links cascade (404 when missing)."""
    try:
        repository.delete_book(conn, book_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/books/bulk-delete")
def delete_books_bulk(
    payload: BulkDeleteIn, conn: sqlite3.Connection = Depends(get_db)
) -> dict[str, int]:
    """Delete many books in one statement; reports the deleted count."""
    deleted = repository.delete_books_bulk(conn, payload.ids)

    return {"deleted": deleted}


@app.post("/genres", response_model=GenreOut, status_code=201)
def create_genre(
    payload: GenreIn, conn: sqlite3.Connection = Depends(get_db)
) -> GenreOut:
    """Create a single genre (409 on taken name)."""
    try:
        genre = repository.create_genre(conn, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return GenreOut(**genre.__dict__)


@app.get("/genres", response_model=list[GenreOut])
def list_genres(conn: sqlite3.Connection = Depends(get_db)) -> list[GenreOut]:
    """List every genre ordered by name."""
    return [GenreOut(**g.__dict__) for g in repository.list_genres(conn)]


@app.post("/books/{book_id}/genres/{genre_id}", status_code=204)
def tag_book(
    book_id: int,
    genre_id: int,
    conn: sqlite3.Connection = Depends(get_db),
) -> None:
    """Link one m:m tag; re-tagging is a no-op (400 on missing refs)."""
    try:
        repository.add_genre_to_book(conn, book_id, genre_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/books/{book_id}/genres/{genre_id}", status_code=204)
def untag_book(
    book_id: int,
    genre_id: int,
    conn: sqlite3.Connection = Depends(get_db),
) -> None:
    """Unlink one m:m tag; missing links delete silently."""
    repository.remove_genre_from_book(conn, book_id, genre_id)


@app.get("/genres/{genre_id}/books", response_model=list[BookOut])
def list_books_by_genre(
    genre_id: int, conn: sqlite3.Connection = Depends(get_db)
) -> list[BookOut]:
    """List every book carrying a genre (m:m read through the junction)."""
    books = repository.list_books(conn, genre_id=genre_id)

    return [_book_out(b) for b in books]
