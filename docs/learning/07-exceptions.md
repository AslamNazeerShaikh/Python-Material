# 07 — Exceptions in Python

What exceptions are, why Python has no checked exceptions, where each
keyword goes, how to raise/handle/define them, when execution halts,
plus edge cases from a C# lens.

## 1. Mental model: C# vs Python

| C# | Python |
|---|---|
| Checked at compile time in Java; C# has only unchecked | All exceptions unchecked. No `throws` clause, no compiler enforcement |
| `try/catch/finally`, `throw`, `using` | `try/except/else/finally`, `raise`, `with` |
| `Exception` base, `SystemException`, `ApplicationException` | `BaseException` root, `Exception` for app errors |
| `catch (Exception ex)` | `except Exception as exc` |
| `throw;` rethrow preserving stack | Bare `raise` inside `except` |
| `throw new ArgumentException(msg)` | `raise ValueError(msg)` |
| `IDisposable` + `using` | Context manager + `with` |

Python rule: raise early on bad public input (`ValueError`), handle
narrowly at the boundary, never use exceptions for normal flow.

## 2. Keywords and syntax

Full shape:

```python
try:
    value = collection[key]
except KeyError as exc:
    raise ValueError(f"missing {key}") from exc
else:
    handle(value)
finally:
    cleanup()
```

| Block | Runs when | C# note |
|---|---|---|
| `try:` | Guarded lines only, keep minimal | Same as C# `try` |
| `except X as e:` | That type (or subclass) raised | C# `catch (X e)` |
| `else:` | No exception in `try` | No C# equivalent; keeps success path out of guarded lines |
| `finally:` | Always, even on return/raise | Same as C# `finally` |
| `raise X(...)` | Throw new | C# `throw new` |
| `raise X from Y` | Explicit chain | C# inner exception |
| Bare `raise` | Rethrow current, keeps traceback | C# `throw;` (not `throw ex;`) |

Minimal patterns:

```python
try:
    number = int(text)
except ValueError:
    number = 0
```

```python
try:
    handle = open("words.txt", encoding="utf-8")
except OSError as exc:
    raise ValueError(f"cannot open words: {exc}") from exc
```

```python
with open("words.txt", encoding="utf-8") as handle:
    data = handle.read()
```

`with` is C# `using`: acquire, run block, release even on error.

### Syntax side-by-side

| Job | C# | Python |
|---|---|---|
| Guard + handle | `try { ... } catch (KeyNotFoundException ex) { ... }` | `try: ... except KeyError as exc: ...` |
| Rethrow keeping the stack | `throw;` (never `throw ex;` — it resets the stack) | Bare `raise` (never `raise exc` — it resets the stack) |
| Chain the cause | `throw new InvalidOperationException(msg, inner);` (inner exception) | `raise ValueError(msg) from exc` |
| Cleanup | `using (var h = Open()) { ... }` | `with open(...) as h:` |
| Success-only path | No equivalent (code after, or a flag) | `else:` runs only when `try` raised nothing |
| Always runs | `finally { ... }` | `finally:` |
| Custom error | `class NotFoundException : Exception { ... }` (name ends `Exception`) | `class NotFoundError(LookupError): ...` (name ends `Error`, derives `Exception`) |
| Test the throw | `Assert.Throws<NotFoundException>(() => Get(...));` (xUnit; NUnit similar) | `with pytest.raises(NotFoundError, match=...):` |

## 3. Built-in hierarchy you must know

```text
BaseException
├── SystemExit        # sys.exit(), not an error. Do not catch.
├── KeyboardInterrupt # Ctrl+C. Do not catch.
├── GeneratorExit     # generator.close(). Do not catch.
└── Exception         # Catch here and below.
    ├── ValueError        # Right type, bad value: int("x"), negative radius.
    ├── TypeError         # Wrong type/arity: 1 + "a", missing arg.
    ├── AttributeError    # Missing attr: obj.nope. EAFP signal.
    ├── NameError         # Unknown variable. Subclass: UnboundLocalError.
    ├── LookupError
    │   ├── KeyError      # mapping[key] missing. C# KeyNotFoundException.
    │   └── IndexError    # seq[i] out of range.
    ├── StopIteration     # Iterator exhausted. Never raise manually.
    ├── RuntimeError      # Generic runtime fault.
    ├── NotImplementedError  # Abstract stub / TODO override.
    ├── ImportError (ModuleNotFoundError)  # Bad import path.
    └── OSError
        ├── FileNotFoundError
        ├── PermissionError
        └── TimeoutError
```

C# mapping cheat sheet: `ArgumentException` becomes `ValueError` or
`TypeError` (value vs type fault); `KeyNotFoundException` becomes
`KeyError`; `NullReferenceException` becomes `AttributeError` or
`TypeError`; `IOException` becomes `OSError` subclasses;
`InvalidOperationException` becomes `RuntimeError`.

Catch `Exception` subclasses only. Catching `BaseException` swallows
`SystemExit` and `KeyboardInterrupt`, breaking Ctrl+C and test runners.

## 4. Checked vs unchecked: Python has only unchecked

Java forces `throws` declarations; C# and Python do not. Any function
can raise anything at any time. The contract lives in the docstring,
not the signature:

```python
def find_second_largest(numbers: list[int]) -> int:
    """Return the second largest distinct value.

    Args:
        numbers: Input values (at least two distinct required).

    Returns:
        The second largest distinct value.

    Raises:
        ValueError: If fewer than two distinct values exist.
    """
    if numbers is None:
        raise ValueError("numbers must not be None")
```

Readers and `mypy` see types; `Raises:` tells them the failure mode.
No `checked` list exists to enforce.

## 5. Raising correctly

```python
if not name:
    raise ValueError("name must not be empty")
```

Chaining keeps the cause (C# inner exception):

```python
try:
    value = collection[key]
except KeyError as exc:
    raise ValueError(f"missing {key}") from exc
```

Suppress a noisy context only when you transfer its detail:

```python
try:
    int(text)
except ValueError:
    raise ValueError(f"bad number {text!r}") from None
```

Rethrow without losing the traceback:

```python
try:
    save(row)
except OSError:
    log()
    raise  # Keeps original stack. Never `raise exc` here.
```

Never `assert` for runtime validation. Asserts strip under `python -O`:

```python
# Wrong: vanishes with -O.
assert numbers is not None

# Correct.
if numbers is None:
    raise ValueError("numbers must not be None")
```

## 6. Custom user-defined exceptions

Derive from `Exception` (never `BaseException`). Name ends `Error`.
Design around what the catcher needs, not where it is raised:

```python
class ValidationError(ValueError):
    """Reject bad input values."""


class NotFoundError(LookupError):
    """Missing entry, with the key attached."""

    def __init__(self, key: str) -> None:
        super().__init__(f"missing {key}")
        self.key = key
```

Usage:

```python
def get_user(users: dict[str, str], key: str) -> str:
    """Return the user for key.

    Raises:
        NotFoundError: If key is absent.
    """
    try:
        return users[key]
    except KeyError as exc:
        raise NotFoundError(key) from exc
```

Rules:

1. One base per area (`DomainError`) so callers catch broadly or
   narrowly.
2. Attach data (`self.key`), not formatted-only strings, so handlers
   can branch.
3. Keep `__init__` compatible with `Exception(message)`; call
   `super().__init__(message)`.
4. Document each in `Raises:`.
5. Test with `pytest.raises(..., match=...)`:

```python
import pytest


def test_missing_key() -> None:
    with pytest.raises(NotFoundError, match="missing amy"):
        get_user({}, "amy")
```

## 7. Halting, pausing, exit codes

- Uncaught exception prints a traceback to stderr and exits nonzero.
  That is the script-halt path; nothing after the raise runs.
- `sys.exit(3)` raises `SystemExit(3)`, unwinding `finally`/`with`
  cleanup, then exits with code 3. Catch it only to add cleanup, then
  re-raise.
- `input("paused...")` pauses for Enter. `time.sleep(n)` pauses for
  seconds. Neither is exception handling; both live in `demos/`, never
  in `src/` library code.
- Library code never calls `sys.exit()`. Raise; let the entry point in
  `demos/` or `main()` decide the exit code.

```python
import sys


def main() -> int:
    """Run the demo, returning an exit code."""
    try:
        run()
    except ValueError as exc:
        print(f"error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## 8. Handling styles: EAFP vs LBYL

C# leans LBYL (check then act). Python leans EAFP (try, handle the
miss), because attributes and keys appear at runtime:

```python
# EAFP: idiomatic when misses are routine.
try:
    value = mapping[key]
except KeyError:
    value = default()
```

```python
# LBYL: better when the check is cheap and the miss is a bug.
if not name:
    raise ValueError("name must not be empty")
```

Keep the `try` body to minimum lines so the `except` clearly owns the
failure. Never wrap a whole function body in one `try`.

## 9. What not to do

```python
# Wrong: swallows SystemExit, KeyboardInterrupt, everything.
try:
    work()
except:  # noqa: E722, and never ship this.
    pass
```

```python
# Wrong: broad catch hiding bugs.
try:
    work()
except Exception:
    pass
```

```python
# Acceptable only at supervised boundaries (thread top, request
# handler): log and continue, narrowly scoped.
try:
    work()
except OSError as exc:
    logger.error("io failed: %s", exc)
```

Unknown type: catch `Exception` once at the boundary, never in library
code. Library handlers catch only types they understand; the entry
point owns the unknown:

```python
# Library: specific only.
try:
    value = mapping[key]
except KeyError as exc:
    raise NotFoundError(key) from exc
```

```python
# Boundary (main, request handler, thread top): unknown allowed.
def main() -> int:
    """Run the demo, returning an exit code."""
    try:
        run()
    except Exception:
        logger.exception("unhandled failure")
        return 1
    return 0
```

Do not guess the type upfront. Let it crash, read the last traceback
line (`ValueError: ...`) or `type(exc).__name__`, then catch that
specific type at the library site.

`contextlib.suppress` is the readable `except: pass` for one expected
type:

```python
import contextlib

with contextlib.suppress(FileNotFoundError):
    log()
```

## 10. Edge cases

1. Order matters: `except ValueError` before `except Exception`.
   Reversed order makes the specific arm dead code.
2. Subclass surprise: `except LookupError` catches `KeyError` and
   `IndexError`. Catch the narrowest type the handler understands.
3. `finally` return swallows: `return` in `finally` discards a pending
   exception or earlier return. Use `finally` for cleanup only.
4. `else` placement: success code goes in `else`, not after more
   guarded lines, so later failures are not misattributed.
5. Generator boundary (PEP 479): `StopIteration` escaping a generator
   frame becomes `RuntimeError`. End generators with `return`, never
   `raise StopIteration`.
6. Exception in `__init__`: object is discarded, `__del__` semantics
   get murky. Prefer validation before allocation or factory
   `classmethod` checks.
7. `raise ... from None` hides forensics. Use only when the new message
   carries the old detail.
8. `BaseException` catch breaks Ctrl+C and `pytest`. If you must
   observe everything (tracing), re-raise immediately.
9. Chained repr grows: `__cause__` and `__context__` print both
   tracebacks. That verbosity is the feature, not noise.
10. Thread top: exceptions do not cross threads. Catch, ship via
    `queue.Queue` or `concurrent.futures`, re-raise on join.

## Next

- [README.md](README.md) — index.
- [03-functions-def.md](03-functions-def.md) — `Raises:` contracts.
- [04-classes-oop.md](04-classes-oop.md) — custom hierarchies.
