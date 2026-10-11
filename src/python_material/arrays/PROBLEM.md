# SecondLargestNumber

Practice: single-pass scan (manual) vs `sorted(set(...))` (builtin).

## Approach

- Manual (`second_largest.py`): track `largest` and `second` in one O(n) pass, skipping duplicates.
- Builtin (`second_largest_builtin.py`): `sorted(set(numbers), reverse=True)[1]` — O(n log n), clearer.

## Complexity

| Version | Time | Space |
|---|---|---|
| Manual | O(n) | O(1) |
| Builtin | O(n log n) | O(n) |

## Edge cases

- Empty / single-element / all-duplicates input → `ValueError`.
- `None` input → `ValueError` (guard on public API).
- Negative numbers work (no zero-initialization trap).
