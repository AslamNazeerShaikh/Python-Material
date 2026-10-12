# Library CRUD API

Practice: raw `sqlite3` SQL (manual) vs ORM-style thinking, served over
HTTP with FastAPI. One domain carries every relationship shape.

## Approach

- Manual (`database.py` + `repository.py`): hand-written DDL/DML with
  `?` placeholders, `Row` factory, `PRAGMA foreign_keys = ON`, and
  `executemany` for bulk paths — no ORM, every statement visible.
- Orchestrated (`service.py`): `LibraryService` behind reader/writer
  Protocols (SOLID seam) — stats via `Counter`, recent-query `deque`,
  multi-step registration with compensation.
- Failed loudly (`errors.py`): `LibraryError` → `NotFoundError` /
  `ConflictError`, all still `ValueError` for old catchers.
- Served (`api.py`): thin FastAPI routes over the service (one
  connection per request), Pydantic shapes at the boundary, Scalar UI
  at `/scalar` — trade-off is explicit SQL vs zero magic.

## Complexity

| Version | Time | Space |
|---|---|---|
| Single CRUD | O(1) keyed reads/writes | O(1) rows |
| Filtered list | O(log n) indexed / O(n) LIKE scan | O(k) matches |
| Bulk insert/delete | One round trip, O(k) rows | O(k) payload |

## Relationships

- 1:1 — `authors` to `author_profiles` (UNIQUE foreign key).
- 1:many — `authors` to `books` (foreign key + `idx_books_author`).
- many:many — `books` to `genres` through `book_genres`.

## Edge cases

- Empty input → `ValueError` (bulk refuses empty batches).
- Single element → same path as bulk of one.
- Duplicates → UNIQUE emails/names/links collapse or raise `ValueError`.
- Missing refs → `ValueError` in repository, 400/404 over HTTP.
- `None` input → `ValueError` (guard on public API).
