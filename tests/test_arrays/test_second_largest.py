"""Tests for second_largest (manual + builtin)."""

import pytest

from python_material.arrays.second_largest import find_second_largest
from python_material.arrays.second_largest_builtin import (
    find_second_largest_builtin,
)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([5, 5, 3], 3),
        ([1, 2], 1),
        ([3, 1, 2], 2),
        ([-1, -1, -4], -4),
        ([7, 3, 7, 5], 5),
    ],
)
@pytest.mark.parametrize("func", [find_second_largest, find_second_largest_builtin])
def test_returns_second_largest_when_duplicates_exist(
    func, values: list[int], expected: int
) -> None:
    """Manual and builtin agree on the second largest distinct value."""
    assert func(values) == expected


@pytest.mark.parametrize("func", [find_second_largest, find_second_largest_builtin])
@pytest.mark.parametrize("bad", [[], [7], [7, 7, 7]])
def test_raises_when_fewer_than_two_distinct_values(func, bad: list[int]) -> None:
    """Both versions reject inputs without two distinct values."""
    with pytest.raises(ValueError, match="two distinct"):
        func(bad)
