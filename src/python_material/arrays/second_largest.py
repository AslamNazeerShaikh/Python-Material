"""Manual single-pass second-largest-distinct finder (practice-first)."""


def find_second_largest(numbers: list[int]) -> int:
    """Return the second largest distinct value in one pass.

    Args:
        numbers: Input values (at least two distinct values required).

    Returns:
        The second largest distinct value.

    Raises:
        ValueError: If numbers is None or has fewer than two distinct values.
    """
    if numbers is None:
        raise ValueError("numbers must not be None")
    largest: int | None = None
    second: int | None = None
    for value in numbers:
        if value == largest:
            continue
        if largest is None or value > largest:
            second, largest = largest, value
        elif second is None or value > second:
            second = value
    if second is None:
        raise ValueError("Need at least two distinct values.")
    return second
