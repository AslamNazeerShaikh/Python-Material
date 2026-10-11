"""Shared enums for practice exercises."""

from enum import Enum


class SortDirection(str, Enum):
    """Sort direction for ordering exercises. Use instead of bool flags."""

    ASCENDING = "ascending"
    DESCENDING = "descending"
