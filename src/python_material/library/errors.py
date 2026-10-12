"""Domain errors: WHAT went wrong, for catchers to branch on.

Hierarchy (inheritance with a job): every error IS a ValueError, so
existing ``except ValueError`` code keeps working (LSP), while new
code can target the precise shape. The API layer maps NotFound to
404, Conflict to 409, and plain ValueError to 400.
"""

from __future__ import annotations


class LibraryError(ValueError):
    """Base of all library failures. Catch-all for the domain."""


class NotFoundError(LibraryError):
    """A referenced row does not exist (missing author/book/genre)."""


class ConflictError(LibraryError):
    """A write collides (taken email/genre, duplicate link target)."""
