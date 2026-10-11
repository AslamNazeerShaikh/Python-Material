"""Tests for vowel_counter (manual + builtin)."""

import pytest

from python_material.strings.vowel_counter import count_unique_vowels
from python_material.strings.vowel_counter_builtin import (
    count_unique_vowels_builtin,
)


@pytest.mark.parametrize("func", [count_unique_vowels, count_unique_vowels_builtin])
@pytest.mark.parametrize(
    ("word", "expected"),
    [("", 0), ("a", 1), ("hello", 2), ("Minneapolis", 4), ("RHYTHM", 0)],
)
def test_counts_unique_vowels_when_given_words(func, word: str, expected: int) -> None:
    """Manual and builtin agree on distinct vowel counts."""
    assert func(word) == expected
