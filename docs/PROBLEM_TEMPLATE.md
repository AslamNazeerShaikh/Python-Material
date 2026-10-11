# PROBLEM.md template

Copy this file to `src/python_material/<category>/<topic>/PROBLEM.md` for each
new exercise.

# <TopicName>

Practice: <manual technique> (manual) vs <stdlib helper> (builtin).

## Approach

- Manual (`<topic>.py`): <how it works, no builtins>.
- Builtin (`<topic>_builtin.py`): <stdlib equivalent> — <trade-off>.

## Complexity

| Version | Time | Space |
|---|---|---|
| Manual | O(?) | O(?) |
| Builtin | O(?) | O(?) |

## Edge cases

- Empty input → <expected>.
- Single element → <expected>.
- Duplicates → <expected>.
- `None` input → `ValueError` (guard on public API).
