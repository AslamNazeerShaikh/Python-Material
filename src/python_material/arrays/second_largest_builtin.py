"""Builtin equivalent kept beside the manual implementation for comparison."""


def find_second_largest_builtin(numbers: list[int]) -> int:
    """Return the second largest distinct value using stdlib sorting.

    Args:
        numbers: Input values (at least two distinct values required).

    Returns:
        The second largest distinct value.

    Raises:
        ValueError: If numbers is None or has fewer than two distinct values.
    """
    if numbers is None:
        raise ValueError("numbers must not be None")
    distinct = sorted(set(numbers), reverse=True)
    if len(distinct) < 2:
        raise ValueError("Need at least two distinct values.")
    return distinct[1]
