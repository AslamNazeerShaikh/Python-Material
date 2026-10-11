"""Tests for custom_sorter (bubble sort + builtin)."""

import pytest

from python_material.arrays.custom_sorter import (
    sort_with_bubble_sort,
    sort_with_builtin,
)
from python_material.common import SortDirection


@pytest.mark.parametrize("func", [sort_with_bubble_sort, sort_with_builtin])
def test_sorts_ascending_when_unsorted(func) -> None:
    """Both sorters order unsorted input ascending."""
    assert func([3, 1, 2]) == [1, 2, 3]


@pytest.mark.parametrize("func", [sort_with_bubble_sort, sort_with_builtin])
def test_sorts_descending_when_direction_descending(func) -> None:
    """Both sorters respect SortDirection.DESCENDING."""
    assert func([1, 3, 2], SortDirection.DESCENDING) == [3, 2, 1]


@pytest.mark.parametrize("func", [sort_with_bubble_sort, sort_with_builtin])
def test_returns_empty_when_input_empty(func) -> None:
    """Empty input yields empty output."""
    assert func([]) == []


@pytest.mark.parametrize("func", [sort_with_bubble_sort, sort_with_builtin])
def test_does_not_mutate_when_given_input(func) -> None:
    """Sorters return new lists and leave the input untouched."""
    values = [3, 1, 2]
    func(values)
    assert values == [3, 1, 2]
