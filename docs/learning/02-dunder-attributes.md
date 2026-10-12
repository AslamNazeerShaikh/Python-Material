# 02 — Dunder Attributes (`__x__`)

What each popular dunder means, why it exists, where it lives, how and
when to use it. Dunder means double-underscore on both sides. Python
reserves the pattern for interpreter protocol. Do not invent your own
`__mine__` names.

## 1. `__name__` and `__main__`

What: `__name__` is the module name the interpreter assigns. `__main__`
is the name of the entry-point script.

Why: replaces C# `static void Main()`. Lets one file act as both
importable library and runnable script.

Where: any module that can run directly.

How:

```python
# src/python_material/arrays/second_largest.py
def main() -> None:
    # Demo-only wiring. Real work stays in pure functions.
    result = find_second_largest([1, 2, 3])
    print(result)


if __name__ == "__main__":
    main()
```

When: always guard script/demo code this way. Library import must not
print, read input, open network, or call `sys.exit()`.

Edge: `python file.py` vs `python -m pkg.file` both set
`__name__ == "__main__"`, but only `-m` sets `__package__` correctly for
absolute imports. Prefer `-m` from the repo root.

## 2. `__init__` (two meanings)

### 2a. `__init__.py` file

What: marks a directory as a package, runs on first import.

Why: package init hook and re-export point.

Where: every package directory in `src/`.

How (keep minimal):

```python
"""Arrays category package."""

from python_material.arrays.second_largest import find_second_largest

__all__ = ["find_second_largest"]
```

When: re-export the public surface only. Never put heavy logic,
I/O, or prints here.

### 2b. `Class.__init__` method

What: instance initializer, closest to a C# constructor but not
identical. `__new__` allocates, `__init__` configures and must return
`None`.

Why: per-instance setup (`this.x = x` becomes `self.x = x`).

Where: inside `class`.

How:

```python
class Point:
    """2D point."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
```

When: validate and assign fields. No overloads; use defaults or
`@classmethod` factories instead.

Edge: forgetting `self.x = x` and only annotating `x: int` at class
level stores nothing. Accessing `obj.x` then raises `AttributeError`.

## 3. `__all__`

What: list of public names for `from module import *`.

Why: keeps wildcard imports clean, documents the public API.

Where: after the docstring, before imports.

How:

```python
__all__ = ["find_second_largest"]
```

When: every exercise module that wants a stable wildcard surface.

Edge: privacy is not enforced. `from m import _helper` still works,
and `import m; m._helper` always works. Linters respect the `_`
convention; the interpreter does not block you.

## 4. `__version__` and `__author__`

What: metadata strings. No meaning to the interpreter.

Why: C# `AssemblyVersion` / `AssemblyCompany` equivalent for humans
and packaging tools.

Where: top-level package `__init__.py`, or better only in
`pyproject.toml`.

How:

```python
__version__ = "0.1.0"
__author__ = "Your Name"
```

When: once per distribution, not once per file. Modern code reads it
with `importlib.metadata.version("package")` instead of duplicating.

Edge: duplicated per-file versions drift. Single source of truth wins.

## 5. Other popular ones you will meet

| Name | C# analogue | Use |
|---|---|---|
| `__doc__` | `<summary>` XML doc | `help(obj)` text from the docstring |
| `__file__` | `Assembly.Location` | Path of the loaded `.py` file |
| `__package__` | Containing namespace | Enables `python -m` relative behavior |
| `__dict__` | Reflection field bag | `obj.__dict__` holds writable instance fields |
| `__class__` | `GetType()` | `obj.__class__` is the runtime type |
| `__bases__`, `__mro__` | Base-type chain | Multiple inheritance order; inspect with `help(Cls)` |
| `__slots__` | Struct layout opt-in | Restricts fields, saves memory; breaks dynamic attrs |
| `__str__`, `__repr__` | `ToString()`, debugger display | Always define `__repr__`; `__str__` for users |
| `__eq__`, `__hash__` | `Equals`, `GetHashCode` | Defining `__eq__` sets `__hash__` to `None` unless defined |
| `__len__`, `__iter__`, `__next__`, `__getitem__` | `IEnumerable`, indexer | `for`, `len()`, `obj[i]` protocol |
| `__call__` | Delegate invocation | Makes `obj()` legal |
| `__enter__`, `__exit__` | `IDisposable` + `using` | `with open(...) as f:` protocol |
| `__bool__` | Truthiness | Controls `if obj:` |

Minimal readable object:

```python
class Point:
    """2D point."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point(x={self.x!r}, y={self.y!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
```

Returning `NotImplemented` (not raising) lets Python try the reflected
operation. That is the correct `__eq__` fallback.

## 6. C# syntax vs Python syntax side-by-side

Same jobs, mirrored spelling. Behavior column says whether the
similarity is real or surface-only.

| Job | C# | Python | Same? |
|---|---|---|---|
| Program entry | `static void Main(string[] args) { ... }` (or top-level statements, C# 9+) | `def main() -> ...: ...` plus `if __name__ == "__main__": main()` | Same job, different shape |
| Doc comment | `/// <summary>...</summary>` with `<param>` / `<returns>` | Docstring `"""..."""` with `Args:` / `Returns:` / `Raises:` | Same job |
| Type identity | `obj.GetType()`, compile-time `typeof(X)` | `type(obj)` / `obj.__class__` (always runtime) | Similar job; `typeof` has no runtime equivalent |
| String form | `ToString()` | `__str__` / `__repr__` (always define `__repr__`) | Same job |
| Equality + hash | `Equals` + `GetHashCode` (keep paired) | `__eq__` + `__hash__` (defining `__eq__` sets `__hash__` to `None`) | Same pairing rule |
| Iteration / indexing | `IEnumerable` + `yield return`, indexer `this[i]` | `__iter__` / `__len__` / `__getitem__` + `yield` | Same shape |
| Cleanup | `IDisposable` + `using` | `__enter__` / `__exit__` + `with` | Same shape |
| Package version | `<Version>` in `.csproj` | `pyproject.toml` (optionally mirrored as `__version__`) | Same job; Python single-sources it |
| Wildcard surface | `using` imports namespaces, never names; no `*` | `__all__` lists the names `from m import *` picks up | Different — Python's surface is explicit per module |

## Next

- [03-functions-def.md](03-functions-def.md) — signatures and calls.
- [04-classes-oop.md](04-classes-oop.md) — full object model.
