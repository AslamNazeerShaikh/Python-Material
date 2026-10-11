"""Manual unique-vowel counter (practice-first)."""


def count_unique_vowels(word: str) -> int:
    """Count distinct vowels in word with an explicit scan.

    Args:
        word: Input word.

    Returns:
        Number of distinct vowels (a, e, i, o, u).

    Raises:
        ValueError: If word is None.
    """
    if word is None:
        raise ValueError("word must not be None")
    seen: set[str] = set()
    for char in word.lower():
        if char in "aeiou":
            seen.add(char)
    return len(seen)
