# 01 — Modules and Packages

What a module is, why files are namespaces, where packages come from, how
to import, when code runs on import.

## 1. What

- Module: one `.py` file. Name is its import path.
  `src/python_material/arrays/second_largest.py` imports as
  `python_material.arrays.second_largest`.
- Package: a directory with `__init__.py` plus its `.py` files.
  The `__init__.py` runs once on first import of anything in the package.
- Namespace package: a directory without `__init__.py` (Python 3.3+).
  Works, but this repo keeps `__init__.py` for explicit packaging and
  tooling support.

```text
src/python_material/
    __init__.py
    common/
        __init__.py
    arrays/
        __init__.py
        second_largest.py
```

## 2. Why this shape

C# resolves types at build from project references. Python resolves
imports at runtime via `sys.path`. The file layout is the API layout, so
a clean folder means a clean API. `__init__.py` is the package hook for
re-exports and version metadata.

## 3. Where to put code

- Library code: `src/python_material/<category>/<topic>/<topic>.py`.
  Pure functions, return values, no `print()`, no `input()`.
- Shared helpers: `src/python_material/common/`.
- Runnable output: `demos/` only, behind
  `if __name__ == "__main__":`.
- Tests mirror the package: `tests/test_<category>/test_<topic>.py`.

## 4. How to import

```python
"""Module docstring first, then dunders, then imports."""

from __future__ import annotations

__all__ = ["find_second_largest"]

import os
import sys

import pytest

from python_material.common import SortDirection
```

Rules followed here (see `docs/STYLE_GUIDE.md`):

1. Top of file only, after docstring and dunders.
2. Groups: stdlib, blank line, third-party, blank line, local.
3. One import per line, absolute paths only, no `from m import *` except
   documented re-export with `__all__`.

Common forms:

```python
import python_material.arrays.second_largest as sl
from python_material.arrays.second_largest import find_second_largest
from python_material import arrays  # the package __init__
```

## 5. When code runs

Import executes the module top to bottom once, then caches it in
`sys.modules`. That means:

```python
# second_largest.py
print("importing")  # Runs once on first import. Do not do this.


def find_second_largest(numbers: list[int]) -> int: ...
```

Guard script behavior:

```python
def main() -> None:
    print(find_second_largest([1, 2, 3]))


if __name__ == "__main__":
    main()
```

## 6. Edge cases

1. Circular imports: `a.py` imports `b.py` which imports `a.py`.
   One of them sees a half-initialized module. Fix by moving the shared
   symbol to `common/`, importing inside the function, or restructuring.
2. Heavy `__init__.py`: importing the package runs it. Database
   connections or prints there slow every import and cause side effects.
   Keep it to re-exports and metadata.
3. Script vs module run: `python second_largest.py` sets `__package__`
   to `None` and breaks absolute imports. Prefer
   `python -m python_material.arrays.second_largest` from the repo root.
4. `from m import *` without `__all__` imports all public names
   (everything not starting with `_`), including imported helpers.
   Define `__all__` to keep wildcard imports clean.
5. Name shadowing stdlib (`email.py`, `random.py`) hijacks imports.
   Never name a module after the stdlib.

## Next

- [02-dunder-attributes.md](02-dunder-attributes.md) — the names with
  double underscores.
- [03-functions-def.md](03-functions-def.md) — declaring behavior.
