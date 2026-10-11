# Python-Material Style Guide — Formatting, Best Practices & Guardrails

**Status: enforceable.** Every code change and every AI review in this repo is
judged against this document. When the `code-reviewer` agent reports a finding,
it cites the section below (e.g. `STYLE_GUIDE §4 imports`).

**Sources** (in precedence order for conflicts — repo consistency wins, per PEP 8's
"foolish consistency" principle):

1. [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) — authoritative base.
2. [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) — strictest deltas adopted (§2–§3).
3. [IST Guide of Best Practices for Python (gist)](https://gist.github.com/ruimaranhao/4e18cbe3dad6f68040c32ed6709090a3) — naming, equality, comprehensions, imports, docs.
4. [Best Python Coding Practices — clean & efficient code (Medium)](https://medium.com/@utkarshshukla.author/best-python-coding-practices-writing-clean-and-efficient-code-4784946a17d0) — constants, globals, venv, tests.

> Consistency within one module/function matters most; consistency within this
> repo beats any single external guide; PEP 8 wins only when the repo has no rule.

---

## §0 Non-negotiable gates (CI checklist)

| # | Gate (metric) | Rule | Source |
|---|---|---|---|
| G0 | Format clean | `ruff format --check .` passes (88-col, double quotes, 4-space) | PEP 8 + Google §3.2/§3.4 |
| G1 | Lint clean | `ruff check .` passes (E/F/W/I/UP/B/C4/SIM) | PEP 8 + Google §2.1 |
| G2 | Types declared | `mypy src` passes; all public signatures fully hinted | Google §2.21 |
| G3 | Tests green | `pytest` passes; coverage ≥ 80% (`fail_under = 80`) | Medium §9 |
| G4 | No secrets | No `.env*`/`*.key`/`*.pem`/`secrets.*`/`credentials.*` touched | repo guardrail |
| G5 | Docstrings present | Public modules/functions/classes documented, Google-style | PEP 257 + Google §3.8 |

Run all five before every commit:

```bash
ruff check --fix . && ruff format . && mypy src && pytest
```

---

## §1 Layout & whitespace

1. **Indent 4 spaces, never tabs.** Continuation lines: align with the opening
   delimiter, or use a 4-space hanging indent with nothing on the first line.
   (PEP 8; Google §3.4; IST "be consistent".)
   ```python
   # Correct.
   total = long_function_name(var_one, var_two, var_three, var_four)
   total = long_function_name(
       var_one, var_two, var_three, var_four
   )
   ```
2. **Max line length 88** (Black/Ruff-compatible; PEP 8 allows 79–99 by team
   agreement — this repo fixes **88**). Docstrings/comments wrap at 72 where
   practical. Break lines with implicit continuation (parentheses), never
   backslashes. Break before binary operators (Knuth style), consistently.
   ```python
   # Correct.
   income = (
       gross_wages
       + taxable_interest
       - ira_deduction
   )
   ```
3. **Blank lines:** two between top-level functions/classes; one between methods
   and after a class docstring; none directly after a `def` line; single blanks
   sparingly inside functions to mark logical sections. (PEP 8; Google §3.5.)
4. **No trailing whitespace. No semicolons.** One statement per line; `if/for/while`
   with bodies go on separate lines. (PEP 8; Google §3.1.)
5. **File encoding UTF-8, no declaration.** ASCII-only identifiers, English words.
   (PEP 8.)
6. **Shebang** `#!/usr/bin/env python3` only on files meant to be executed
   directly (e.g. `demos/main.py`). (Google §3.7.)

## §2 Quotes & trailing commas

1. **Double quotes** for all strings; triple-double-quotes for docstrings.
   (Single source rule from Google/Black; PEP 8 permits either but demands
   consistency — this repo fixes double.)
2. **Trailing commas:** required for single-element tuples `("setup.cfg",)`;
   recommended when a multi-line collection puts one item per line with the
   bracket on its own line; forbidden on the same line as the closing bracket.
   ```python
   # Correct.
   FILES = [
       "setup.cfg",
       "tox.ini",
   ]
   ```

## §3 Spacing & operators

1. No space inside `()[]{}`; no space before `, ; :`; one space after them
   (except at line end).
2. One space around `=`, comparisons, `and/or/not`. Judge arithmetic spacing for
   lowest-precedence clarity, never more than one space, equal on both sides.
   ```python
   # Correct.
   submitted += 1
   hypot2 = x * x + y * y
   c = (a + b) * (a - b)
   ```
3. **No spaces** around `=` in keyword args / unannotated defaults;
   **use spaces** when the parameter has an annotation:
   ```python
   # Correct.
   def complex_number(real: float, imag: float = 0.0) -> complex: ...
   result = compute(value, scale=2)
   ```
4. Never vertically align tokens across lines (`x = 1` / `long_var = 2` padded) —
   maintenance burden. (Google §3.6.)

## §4 Imports (strict)

1. **Top of file only**, after module docstring/dunders, before globals. Order:
   **stdlib → third-party → local**, one blank line between groups.
   (PEP 8; IST; Google §2.2.)
2. **One import per line** (`import os` + `import sys`, never `import sys, os`).
   `from x import y` only where `x` is the package prefix and `y` a module —
   **import modules, not individual symbols**, except `typing` /
   `collections.abc` / `dataclasses` / `enum` (Google §2.2.4.1 exemption).
   ```python
   # Correct.
   import os
   import sys

   import pytest

   from python_material.common import SortDirection
   ```
3. **Absolute imports only** — no relative `from . import x`, no bare `import jodie`.
   No wildcard `from m import *` (except republishing a documented public API
   with `__all__`). No unused imports. (PEP 8; Google §2.2–§2.3.)
4. **Module dunders** (`__all__`, `__version__`, `__author__`) go after the
   docstring, before imports (except `from __future__`). (PEP 8.)

## §5 Naming (strict)

| Target | Convention | Example | Source |
|---|---|---|---|
| Packages/modules | short `lowercase`, `_` ok | `second_largest.py` | PEP 8 |
| Functions/variables/args | `lower_case_with_underscores` | `find_second_largest` | PEP 8 + IST + Medium |
| Classes/exceptions | `CapWords`; exceptions end `Error` | `SortDirection`, `ValidationError` | PEP 8 + Google §2.4 |
| Constants | `ALL_CAPS_WITH_UNDERSCORES` | `MAX_RETRIES = 3` | PEP 8 + IST + Medium |
| Type vars | `CapWords`, short (`T`, `AnyStr`), `+_co`/`_contra` | `VT_co` | PEP 8 |
| Non-public | `_single_leading_underscore` | `_cache` | PEP 8 + IST |
| Name-mangled | `__double_leading` (avoid-clash only) | `__buffer` | PEP 8 |
| Keyword clash | single trailing `_` | `class_` | PEP 8 |
| `self` / `cls` | always first arg names | `def method(self)` | PEP 8 |

1. **Never** `l`, `O`, `I` as single-char names. Avoid redundant labeling
   (`audio.Core`, not `audio.AudioCore`); prefer reverse notation
   (`elements_active`, not `active_elements`). (IST.)
2. **No `mixedCase`** — this repo has no legacy `threading.py`-style exception.
3. **Use `SortDirection` enum, never `bool` flags** for direction-like params
   (repo convention, `src/python_material/common/`).

## §6 Truthiness, comparisons & types

1. **`is None` / `is not None`** for `None`; never `== None`. Never `== True` /
   `== False` / `is True`. (PEP 8; IST; Google §2.14.)
   ```python
   # Correct.
   if value is None:
       value = []
   if greeting:
       send(greeting)
   ```
2. **Implicit false** for sequences: `if seq:` / `if not seq:`, never
   `if len(seq):`. For integers compare explicitly (`i % 10 == 0`), since
   `None` is falsy too. (Google §2.14.)
3. **`isinstance()`** for type checks, never `type(x) is type(1)`. (PEP 8.)
4. **`startswith()`/`endswith()`**, never slicing, for affix checks. (PEP 8.)
5. **Empty containers are false** — but `'0'` is true; NumPy arrays need `.size`.
   (Google §2.14.)

## §7 Comments & docstrings (strict)

1. **Docstrings mandatory** for every public module, function, class, method
   (PEP 257 + Google §3.8). Triple-double-quotes; one-line summary ≤ 88 chars
   ending in `.`/`?`/`!`; blank line, then detail. Sections `Args:` / `Returns:`
   / `Raises:` with 4-space hanging indent, consistent per file:
   ```python
   """Return the second largest distinct value.

   Args:
       numbers: Input values (at least two distinct required).

   Returns:
       The second largest distinct value.

   Raises:
       ValueError: If fewer than two distinct values exist.
   """
   ```
2. **Comments are complete sentences**, first word capitalized, `#` + one space.
   Block comments indent with the code; inline comments need ≥ 2 spaces before
   `#` and must add information (`x += 1  # Compensate for border`, never
   `# Increment x`). Use sparingly — prefer small named functions over
   explanatory comments (IST). Keep comments truthful: contradicting comments
   are worse than none.
3. **No `print()` in library code** — return values; `demos/` owns output.
   (Repo rule.)

## §8 Functions, comprehensions & generators

1. **`def`, never `f = lambda x: ...`** for named functions (tracebacks need
   names). Lambdas OK for one-liners ≤ ~60–80 chars; prefer `operator.*` and
   generator expressions over `map`/`filter` + lambda. (PEP 8; Google §2.10.)
2. **Comprehensions for simple cases only**: one `for` + optional filter.
   Multiple `for` clauses or stacked filters → explicit loops. (Google §2.7;
   IST; Medium.)
   ```python
   # Correct.
   squares = [x ** 2 for x in range(11) if x % 2 == 0]
   # Wrong — refactor to nested loops.
   pairs = [(x, y) for x in range(10) for y in range(5) if x * y > 10]
   ```
3. **Ternaries only when each part fits one line**; else a full `if`. Break
   before `else` at the same level. (Google §2.11.)
4. **Default args must be immutable** (`None` + guard, or `()`). Never
   `def f(items=[])`, never `time.time()` / flag values as defaults.
   (Google §2.12.)
   ```python
   # Correct.
   def collect(items: list[int] | None = None) -> list[int]:
       if items is None:
           items = []
       return items
   ```
5. **Type hints on all public signatures** (args + return), `X | None` style;
   variable annotations `name: type` (no space before colon, one after).
   Keep hints current; stub (`.pyi`) only for third-party shims. (Google §2.21.)
6. **Consistent `return`s**: all paths return a value, or none do; an
   expression-returning function ends with an explicit `return None`-capable
   path, never a bare `return` mid-function. (PEP 8.)
7. **Generators**: document with `Yields:`, not `Returns:`; force cleanup of
   managed resources (context manager). (Google §2.9.)
8. **Properties/`@property` only** for cheap, unsurprising derivations — never to
   wrap trivial get/set (make the attribute public instead); never for expensive
   computation (callers assume attribute access is cheap). (Google §2.13.)
9. **Decorators judiciously**: document "this is a decorator", unit-test it, no
   external deps at import time. No `staticmethod` (use module functions);
   `classmethod` only for named constructors / class-state routines.
   (Google §2.17.)

## §9 Errors, resources & state

1. **Narrow `try`, specific `except`.** `try` body = minimum lines; catch
   `ValueError`/`KeyError`/explicit OS errors, never bare `except:` or
   `except Exception:` unless re-raising or building a supervised isolation
   point (log + suppress at a thread boundary). Never use `assert` for runtime
   validation — asserts are strippable; raise properly. (PEP 8; Google §2.4.)
   ```python
   # Correct.
   try:
       value = collection[key]
   except KeyError:
       return key_not_found(key)
   else:
       return handle_value(value)
   ```
2. **`raise X from Y`** for explicit chaining; `raise X from None` only when
   details are transferred to the new message. Derive custom exceptions from
   `Exception` (not `BaseException`); design hierarchies around what catchers
   need ("what went wrong"), not where raised. (PEP 8; Google §2.4.)
3. **`with` for local resources** (files, locks, transactions); `try/finally`
   acceptable. Context managers that do more than acquire/release get their own
   named function. (PEP 8; Google §2.4; IST.)
   ```python
   # Correct.
   with open("words.txt", encoding="utf-8") as handle:
       data = handle.read()
   ```
4. **No mutable global state.** Constants (`UPPER_SNAKE`) at module level;
   anything mutable is `_private` + accessed via functions/methods, with a
   comment justifying it. (Google §2.5; Medium §6.)
5. **No magic numbers** — name every literal (`PI = 3.14159`, `PORT_MIN = 1024`).
   (Medium §3.)

## §10 Performance & Pythonic idioms

1. **Join, don't concatenate in loops**: `"".join(parts)`, never `s += piece`
   (CPython-only optimization; quadratic elsewhere). (PEP 8.)
2. **Default iterators/operators**: `for key in mapping`, `if x in items`,
   `for line in handle`, `for k, v in mapping.items()` — never `.keys()` /
   `.readlines()` loops; never mutate a container while iterating it.
   (Google §2.8.)
3. **EAFP with narrow scope**, rich comparisons complete (`functools.total_ordering`
   when defining ordering), f-strings for formatting, `pathlib` for paths,
   `datetime.now(timezone.utc)` (naive datetimes forbidden). (PEP 8 + repo.)
4. **No power features**: no metaclasses, bytecode tricks, import hacks,
   `getattr`-reflection spaghetti, `__del__` cleanup. Stdlib power tools
   (`dataclasses`, `enum`, `abc`) are fine. (Google §2.19.)
5. **Threading**: never rely on GIL-atomicity; `queue.Queue` between threads,
   `threading` primitives otherwise. (Google §2.18.)

## §11 Testing, venv & hygiene (Medium + repo)

1. **pytest for everything new** — one module per topic, parametrized edge cases
   first (`test_<behavior>_when_<condition>`); `pytest.raises(..., match=...)`
   for error paths. (Medium §9.)
2. **Virtualenv per project**: `python -m venv .venv && source .venv/bin/activate`
   (Windows: `.venv\\Scripts\\activate`); never install packages globally or
   from agents without explicit user approval. (Medium §8.)
3. **Pure library**: no `print()`/`input()` in `src/`; no `sys.exit()` in
   importable code; demos live in `demos/` behind `if __name__ == "__main__":`.
4. **Fix fast**: broken lint/type/test/doc on discovery, same change — "now is
   better than never". (PEP 20 via IST.)

## §12 Review protocol (for humans & AI reviewers)

1. Review **against this file**, section by section (§1–§11). Each finding cites
   its section: `STYLE_GUIDE §4 imports (absolute-only)`.
2. Verdicts: **Block** (G0–G5 gate failure, wrong behavior, secret risk) vs
   **Nit** (wording, micro-style with equal alternatives).
3. Report as a table: `Check (metric) | Pass/Fail | Evidence (file:line) |
   Guide section`. No drive-by rewrites outside the finding.
4. Suggest the minimal conforming fix (diff-shaped), don't restyle passing code.

## Changelog

| Date (UTC) | Change | Source |
|---|---|---|
| 2026-10-11 | Initial guide: PEP 8 lay-out/naming/programming + Google strict deltas + IST naming/equality/docs + Medium constants/globals/venv/tests | PEP 8; Google pyguide; IST gist `4e18cbe`; Medium `4784946a17d0` |
