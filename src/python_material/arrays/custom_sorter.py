"""Manual bubble-sort vs builtin sort (practice-first)."""

from python_material.common import SortDirection


def sort_with_bubble_sort(
    values: list[int], direction: SortDirection = SortDirection.ASCENDING
) -> list[int]:
    """Sort values with bubble sort, returning a new list.

    Args:
        values: Input values (not mutated).
        direction: Sort direction (never a bool flag).

    Returns:
        A new sorted list.

    Raises:
        ValueError: If values is None.
    """
    if values is None:
        raise ValueError("values must not be None")

    # Work on a copy so the caller's list is never mutated.
    items = list(values)

    # Bubble the largest unsorted value to its slot each pass.
    for end in range(len(items) - 1, 0, -1):
        for i in range(end):
            out_of_order = (
                items[i] > items[i + 1]
                if direction == SortDirection.ASCENDING
                else items[i] < items[i + 1]
            )
            if out_of_order:
                items[i], items[i + 1] = items[i + 1], items[i]

    return items


def sort_with_builtin(
    values: list[int], direction: SortDirection = SortDirection.ASCENDING
) -> list[int]:
    """Sort values with the stdlib (Timsort), returning a new list.

    Args:
        values: Input values (not mutated).
        direction: Sort direction (never a bool flag).

    Returns:
        A new sorted list.

    Raises:
        ValueError: If values is None.
    """
    if values is None:
        raise ValueError("values must not be None")

    return sorted(values, reverse=direction == SortDirection.DESCENDING)
