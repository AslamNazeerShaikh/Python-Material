"""Repository tests over throwaway databases (never the committed seed)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from python_material.library import database, repository


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    """Yield an initialized, seeded connection on a temp file."""
    db = database.connect(tmp_path / "test.db")
    database.init_db(db)
    database.seed(db)
    yield db
    db.close()


def test_seed_shape(conn: sqlite3.Connection) -> None:
    assert len(repository.list_authors(conn)) == 3
    assert len(repository.list_books(conn)) == 5
    assert len(repository.list_genres(conn)) == 4


def test_one_to_one_optional_side(conn: sqlite3.Connection) -> None:
    alan = next(a for a in repository.list_authors(conn) if a.name == "Alan Turing")
    assert repository.get_profile(conn, alan.id) is None

    profile = repository.upsert_profile(conn, alan.id, "Enigma codebreaker.")
    assert profile.bio == "Enigma codebreaker."
    assert repository.upsert_profile(conn, alan.id, "Second bio").bio == "Second bio"


def test_one_to_many_detail(conn: sqlite3.Connection) -> None:
    ada = next(a for a in repository.list_authors(conn) if a.name == "Ada Lovelace")
    detail = repository.get_author_detail(conn, ada.id)

    assert detail is not None
    assert detail.bio is not None
    assert [b.title for b in detail.books] == [
        "Notes on the Engine",
        "Sketch Collection",
    ]


def test_many_to_many_detail(conn: sqlite3.Connection) -> None:
    book = next(
        b for b in repository.list_books(conn) if b.title == "Machine Intelligence"
    )
    detail = repository.get_book_detail(conn, book.id)

    assert detail is not None
    assert detail.author_name == "Alan Turing"
    assert detail.genres == ("Essay", "Science Fiction")


def test_bulk_create_and_bulk_delete(conn: sqlite3.Connection) -> None:
    authors = repository.create_authors_bulk(
        conn, [("Katherine J.", "kj@example.com"), ("Radia P.", "rp@example.com")]
    )
    assert [a.email for a in authors] == ["kj@example.com", "rp@example.com"]

    made = repository.create_books_bulk(
        conn, [("Net", 1990, authors[0].id), ("Perl", 1987, authors[1].id)]
    )
    assert len(made) == 2

    assert repository.delete_books_bulk(conn, [b.id for b in made]) == 2
    assert repository.delete_books_bulk(conn, []) == 0


def test_bulk_rolls_back_on_missing_author(conn: sqlite3.Connection) -> None:
    before = len(repository.list_books(conn))
    with pytest.raises(ValueError, match="authors not found"):
        repository.create_books_bulk(conn, [("Ghost", 2000, 4242)])

    assert len(repository.list_books(conn)) == before


def test_unique_violations_become_value_error(conn: sqlite3.Connection) -> None:
    with pytest.raises(ValueError, match="already taken"):
        repository.create_author(conn, "Clone", "ada@example.com")
    with pytest.raises(ValueError, match="already taken"):
        repository.create_genre(conn, "Essay")


def test_search_escapes_wildcards(conn: sqlite3.Connection) -> None:
    assert repository.list_books(conn, query="100%") == []
    assert len(repository.list_books(conn, query="comp")) == 2


def test_cascade_delete_author(conn: sqlite3.Connection) -> None:
    ada = next(a for a in repository.list_authors(conn) if a.name == "Ada Lovelace")
    repository.delete_author(conn, ada.id)

    assert repository.get_author(conn, ada.id) is None
    assert repository.list_books(conn, author_id=ada.id) == []
    assert repository.get_profile(conn, ada.id) is None


def test_tag_round_trip(conn: sqlite3.Connection) -> None:
    book = repository.list_books(conn, query="Computable")[0]
    essay = next(g for g in repository.list_genres(conn) if g.name == "Essay")

    repository.add_genre_to_book(conn, book.id, essay.id)
    repository.add_genre_to_book(conn, book.id, essay.id)
    detail = repository.get_book_detail(conn, book.id)
    assert detail is not None and detail.genres == ("Essay", "Mathematics")

    repository.remove_genre_from_book(conn, book.id, essay.id)
    detail = repository.get_book_detail(conn, book.id)
    assert detail is not None and detail.genres == ("Mathematics",)


def test_missing_rows_raise(conn: sqlite3.Connection) -> None:
    with pytest.raises(ValueError, match="not found"):
        repository.delete_book(conn, 4242)
    with pytest.raises(ValueError, match="not found"):
        repository.delete_author(conn, 4242)
    with pytest.raises(ValueError, match="not found"):
        repository.update_book(conn, 4242, title="Ghost")


def test_indexes_exist(conn: sqlite3.Connection) -> None:
    names = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")
    }

    assert {"idx_books_author", "idx_books_year", "idx_book_genres_genre"} <= names
