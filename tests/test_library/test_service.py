"""Service tests: orchestration, stats, Protocols, error shapes."""

from __future__ import annotations

from pathlib import Path

import pytest

from python_material.library import database, repository
from python_material.library.errors import (
    ConflictError,
    LibraryError,
    NotFoundError,
)
from python_material.library.service import (
    CatalogReader,
    CatalogWriter,
    LibraryService,
)


@pytest.fixture()
def service(tmp_path: Path) -> LibraryService:
    """Yield a seeded service on a temp file (conn owned by the test)."""
    db = database.connect(tmp_path / "svc.db")
    database.init_db(db)
    database.seed(db)
    yield LibraryService(db)
    db.close()


def test_service_satisfies_both_protocols(service: LibraryService) -> None:
    assert isinstance(service, CatalogReader)
    assert isinstance(service, CatalogWriter)


def test_books_per_author_ranking(service: LibraryService) -> None:
    assert service.books_per_author() == [
        ("Ada Lovelace", 2),
        ("Alan Turing", 2),
        ("Grace Hopper", 1),
    ]


def test_recent_queries_log_and_snapshot(service: LibraryService) -> None:
    assert service.recent_queries == ()

    service.list_books(query="engine")
    service.list_books(query="tales")
    service.list_books()

    assert service.recent_queries == ("engine", "tales")


def test_register_flow_and_compensation(service: LibraryService) -> None:
    detail = service.register_author_with_books(
        "Octavia B.", "ob@example.com", [("Kindred", 1979), ("Dawn", 1987)]
    )
    assert detail.book_count == 2

    with pytest.raises(ValueError, match="positive year"):
        service.register_author_with_books(
            "Doomed", "doomed@example.com", [("Bad", -1)]
        )

    names = [a.name for a in service.list_authors()]
    assert "Doomed" not in names


def test_domain_errors_are_value_errors(service: LibraryService) -> None:
    """LSP: every domain error still satisfies except ValueError."""
    with pytest.raises(ValueError, match="already taken"):
        service.create_author("Clone", "ada@example.com")
    with pytest.raises(ValueError, match="not found"):
        service.delete_book(4242)

    assert issubclass(ConflictError, LibraryError)
    assert issubclass(NotFoundError, LibraryError)
    assert issubclass(LibraryError, ValueError)


def test_missing_details_return_none(tmp_path: Path) -> None:
    conn = database.connect(tmp_path / "shapes.db")
    database.init_db(conn)
    try:
        assert repository.get_book_detail(conn, 4242) is None
        assert repository.get_author_detail(conn, 4242) is None
    finally:
        conn.close()
