"""Library CRUD tour on a throwaway database (demos own all prints)."""

import tempfile
from pathlib import Path

from python_material.library import database, repository


def main() -> None:
    """Seed a temp copy, tour single and bulk CRUD, then throw it away."""
    with tempfile.TemporaryDirectory(prefix="library-demo-") as tmp:
        conn = database.connect(Path(tmp) / "tour.db")
        try:
            database.init_db(conn)
            counts = database.seed(conn)
            print(f"seeded: {counts}")

            ada = repository.create_author(conn, "Demo Author", "demo@example.com")
            print(f"created author: {ada}")

            bulk = repository.create_books_bulk(
                conn, [("Demo One", 2020, ada.id), ("Demo Two", 2021, ada.id)]
            )
            print(f"bulk created {len(bulk)} books")

            detail = repository.get_author_detail(conn, ada.id)
            print(f"author detail: {detail}")

            found = repository.list_books(conn, query="demo")
            print(f"search hits: {len(found)}")

            print(
                f"bulk deleted: {repository.delete_books_bulk(conn, [b.id for b in bulk])}"
            )
            repository.delete_author(conn, ada.id)
            print(f"authors left: {len(repository.list_authors(conn))}")
        finally:
            conn.close()


if __name__ == "__main__":
    main()
