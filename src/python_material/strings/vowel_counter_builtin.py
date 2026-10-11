"""Set-comprehension equivalent kept beside the manual implementation."""


def count_unique_vowels_builtin(word: str) -> int:
    """Count distinct vowels in word using a set comprehension.

    Args:
        word: Input word.

    Returns:
        Number of distinct vowels (a, e, i, o, u).

    Raises:
        ValueError: If word is None.
    """
    if word is None:
        raise ValueError("word must not be None")

    return len({char for char in word.lower() if char in "aeiou"})
