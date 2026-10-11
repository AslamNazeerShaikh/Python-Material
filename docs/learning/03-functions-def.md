# 03 — Functions with `def`

How to declare functions and methods, how parameters and arguments work,
what returns, and where C# habits break.

## 1. Basic shape

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

    # Track the two best distinct values seen so far.
    largest: int | None = None
    second: int | None = None

    # Single pass: promote on a new max, else update the runner-up.
    for value in numbers:
        if value == largest:
            continue
        if largest is None or value > largest:
            second = largest
            largest = value
        elif second is None or value > second:
            second = value

    if second is None:
        raise ValueError("Need at least two distinct values.")

    return second
```

Rules: `def` name, parenthesized params, `-> return` hint, colon,
4-space body. Public signatures always hinted. Docstring mandatory.

## 2. Parameters vs arguments

Parameter is the declaration (`def f(a, b=10)`), argument is the call
value (`f(1, 2)`). Python adds kinds C# does not have by default:

```python
def f(a, b=10, *args: int, c: int, d: int = 5, **kwargs: str) -> None:
    """Show every parameter kind."""
```

| Kind | Example | Call rule |
|---|---|---|
| Required positional-or-keyword | `a` | `f(1)` or `f(a=1)` |
| Defaulted | `b=10` | May omit; immutable defaults only |
| Variadic positional (`*args`) | C# `params int[]` | Extra positionals arrive as tuple |
| Keyword-only (after `*args` or bare `*`) | `c`, `d=5` | Must write `c=...` |
| Variadic keyword (`**kwargs`) | Extra named args | Arrive as `dict` |

```python
f(1)  # a=1
f(1, 2, 3, 4, c=9)  # args=(3, 4)
f(1, c=9, extra="hi")  # kwargs={"extra": "hi"}
```

Positional-only (left of `/`) and the `SortDirection` rule:

```python
def sort_items(values: list[int], direction) -> list[int]: ...


def f(a, b, /, c): ...  # a, b cannot be passed as keywords
```

This repo uses the `SortDirection` enum, never a `bool` flag, for
direction-like params.

## 3. Returns

- No `return` or bare `return` gives `None` (`-> None`, like `void`
  but a real value).
- `return a, b` returns one `tuple`, not two values.
- Keep returns consistent: all paths return a value or none do. Never
  a bare `return` mid-function in a value-returning function.
- Generators use `yield` and document `Yields:`, not `Returns:`.

```python
def gen() -> int:
    """Yield is C# yield return."""
    yield 1
    yield 2
```

`async def` is C# `async`: must be awaited, driven by `asyncio.run()`.

## 4. Other function forms

```python
square = lambda x: x * 2  # C# x => x * 2. Expression only.
```

Prefer `def` for named functions (tracebacks need names). Lambdas only
for short one-liners. Nested `def` plus closures replace many C#
lambdas capturing locals.

Decorators are wrappers, like attributes with behavior:

```python
import functools


def log_calls(fn):
    """Decorator: document that this is a decorator and test it."""
    import functools

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
```

Built-ins you will use: `@property`, `@classmethod`, `@staticmethod`,
`@functools.lru_cache`, `@dataclass`.

## 5. Edge cases

1. Mutable default shares state:

   ```python
   # Wrong: one list reused across calls.
   def collect(items: list[int] = []) -> list[int]:
       items.append(1)
       return items


   # Correct.
   def collect(items: list[int] | None = None) -> list[int]:
       if items is None:
           items = []
       items.append(1)
       return items
   ```

2. Late-binding closure: `[lambda: i for i in range(3)]` all see the
   final `i`. Fix with `lambda i=i: i`.
3. Redefinition wins: two `def foo()` blocks keep only the last. There
   is no overload resolution. Use defaults, `X | Y` unions, or
   `@singledispatch` for type-based dispatch.
4. Hints are unchecked at runtime: `def f(x: int)` accepts `str`
   unless `mypy` or manual guards stop it. Validate public input with
   `ValueError`.
5. `"".join(parts)` in loops, never `s += piece` (quadratic elsewhere).
6. Comprehensions for one `for` plus optional filter only. Nested
   loops go explicit.

## 6. Docstring and blank-line shape

No blank line between `def ...:`, the docstring, and the first
statement. The three form one header block:

```python
def find_second_largest(numbers: list[int]) -> int:
    """Return the second largest distinct value."""
    if numbers is None:
        raise ValueError("numbers must not be None")
```

Blank lines separate logical blocks only (guard, setup, computation,
post-check, return), exactly one between each. A blank line after the
docstring orphans the guard from its header (`STYLE_GUIDE §1.4`).

Docstring shape (`STYLE_GUIDE §7.1`):

1. Opening `"""` stays on the summary line, never alone on its own
   line. Leading-newline form breaks `help()` one-line summaries.
2. Summary line first, then blank line, then detail plus `Args:` /
   `Returns:` / `Raises:` sections.
3. One blank line after a class docstring before the first method;
   never inside a function.
4. Floating triple-quoted strings are not comments. Multi-line comments
   use `#` lines; docstrings are reserved for the first statement.

## Next

- [04-classes-oop.md](04-classes-oop.md) — methods are functions with
  `self`.
- [00-csharp-to-python.md](00-csharp-to-python.md) — back to the map.
