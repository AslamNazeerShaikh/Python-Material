# 08 — C# Keywords to Python: `this`, `static`, Passing, Defaults, Lifetime, Scope

Plain-English answers for a C# developer. Each section is one keyword
question: what C# does, what Python does instead, and the edge that
bites.

## 1. `this` → `self` (explicit, always first)

C# passes `this` implicitly. Python makes it the first parameter name,
by convention `self`:

```python
class Dog:
    """Dog."""

    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        """Return the sound."""
        return f"{self.name} says woof"
```

```python
d = Dog("rex")
d.speak()  # Sugar for Dog.speak(d).
```

Human version: Python never hides the receiver. If you see a method
without `self` as first param, it is `@staticmethod` or broken.

Edge: `self` is convention, not keyword. Renaming works but breaks
every reader and linter. `cls` plays the same role for classmethods.

## 2. `static` → three separate ideas

C# `static` means four things; Python splits them:

| C# `static` | Python | Example |
|---|---|---|
| Static method | `@staticmethod` (rare) or module function (preferred) | Stateless helper |
| Static field / singleton state | Class attribute or module constant | `count: int = 0` on class |
| Static class | Module with functions | `math.py` is the static class |
| Extension method | Plain function or `Protocol` | `loud(dog)` not `dog.loud()` |

```python
count: int = 0  # Module-level constant-ish. UPPER_SNAKE by convention.

TOTAL: int = 0


class Point:
    """Point with shared count."""

    count = 0  # Class attribute: one copy shared by instances.

    def __init__(self, x: int) -> None:
        self.x = x
        Point.count += 1

    @staticmethod
    def is_origin(x: int) -> bool:
        """Stateless check. Module function usually reads better."""
        return x == 0
```

Prefer module functions over `@staticmethod` (repo rule). Use
`@classmethod` for named constructors, not statics.

## 3. Pass by value vs reference: neither, it is assignment

C# has value types (copied) and reference types (`ref`/`out` opt-in).
Python has one rule: arguments are object references passed by
assignment. Rebinding the name never affects the caller; mutating the
object does:

```python
def rebinding(items: list[int]) -> None:
    """Rebind locally. Caller sees nothing."""
    items = [9]


def mutating(items: list[int]) -> None:
    """Mutate in place. Caller sees it."""
    items.append(9)
```

```python
xs = [1]
rebinding(xs)  # xs still [1].
mutating(xs)  # xs now [1, 9].
```

Human version: the parameter name is a sticky note on the same object.
Peeling it off (`=`) is private; writing on the object (`.append`,
`obj.x =`) is public.

Edges:

1. Immutable objects (`int`, `str`, `tuple`) cannot be mutated, so
   `x += 1` inside a function rebinds locally. Caller unchanged.
2. `None` default plus guard beats mutable defaults (see `§5`).
3. No `ref`/`out`. Return tuples or a small dataclass instead:
   `return total, count`.

## 4. Constructors and destructors

Constructor is two steps: `__new__` allocates, `__init__` configures.
You write `__init__` 99% of the time:

```python
class Point:
    """Point."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        if x < 0:
            raise ValueError("x must be >= 0")
        self.x = x
        self.y = y
```

There is no destructor equivalent to C# `~Class` / `IDisposable`.
`__del__` exists but runs unpredictably under garbage collection
(cycles, interpreter shutdown). Never use it for cleanup. Use
`with` plus `__enter__`/`__exit__`, or explicit `close()`:

```python
with open("words.txt", encoding="utf-8") as handle:
    data = handle.read()
```

Edge: `__init__` must return `None`. Need to veto creation
(singleton, cached instance)? Override `__new__`, rarely.

## 5. Default, optional, skippable parameters

```python
def greet(name: str, greeting: str = "hello", *args: int, tag: str, **kw: str) -> str:
    """Show every parameter kind."""
    return f"{greeting} {name}"
```

| C# | Python |
|---|---|
| Optional arg `void F(int x = 3)` | Same shape: `def f(x: int = 3)` |
| Named args `F(x: 1)` | Same: `f(x=1)`, plus keyword-only after `*` |
| `params int[]` | `*args` tuple |
| Overloads `F(int)` / `F(string)` | One `def`, defaults and unions. Last def wins |

Skippable middle parameters use keywords at the call:

```python
greet("amy", tag="t")  # greeting keeps default.
```

Rules: immutable defaults only (`None`, `0`, `""`, `()`). Mutable
default shares one object across calls:

```python
# Wrong: one list reused.
def collect(items: list[int] = []) -> list[int]:
    items.append(1)
    return items


# Correct: sentinel plus guard.
def collect(items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    items.append(1)
    return items
```

Keyword-only (after `*`) forces clarity like C# named args;
positional-only (before `/`) locks API shape. This repo uses the
`SortDirection` enum instead of bool flags for direction params.

## 6. `readonly` fields: convention plus three tools

No `readonly` keyword. Options in strength order:

1. Public attribute, don't reassign (weakest, most common).
2. `@property` without setter: attribute error on write.
3. `@dataclass(frozen=True)`: blocks all field writes.
4. `typing.Final`: checker-only promise, no runtime block.

```python
from dataclasses import dataclass
from typing import Final


class Circle:
    """Property-based read-only diameter."""

    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def diameter(self) -> float:
        """Derived, no setter: writing raises AttributeError."""
        return self._radius * 2


@dataclass(frozen=True)
class PointData:
    """Frozen: assigning .x raises FrozenInstanceError."""

    x: int
    y: int


MAX_SIZE: Final = 100  # Type-checker promise. Runtime still writable.
```

Human version: Python trusts adults. `Final` and `_private` are signs,
`@property` and frozen dataclasses are fences. Pick fences for public
API invariants (negative radius), signs for internals.

## 7. Mutable vs immutable: names, not variables

Python has no variable boxes. Names are references to objects, and
objects carry mutability:

| Immutable (new object on change) | Mutable (in-place change) |
|---|---|
| `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `None` | `list`, `dict`, `set`, `bytearray`, most class instances |

```python
a = (1, 2)
b = a  # Same tuple object.
a = a + (3,)  # New tuple. b still (1, 2).
```

```python
a = [1, 2]
b = a  # Same list object.
a.append(3)  # b sees [1, 2, 3]. Shared mutation.
```

Edge that bites C# devs: tuple holding a list is "immutable" only
shallowly. The tuple cannot be resized, but its list item mutates.

## 8. Global vs local scope (LEGB)

Lookup order: Local, Enclosing, Global, Builtin.

```python
sep: str = ","  # Module global. UPPER or lower? Constants UPPER_SNAKE.


def join(values: list[int]) -> str:
    """Local total shadows nothing; reads global sep."""
    total = ",".join(str(v) for v in values)
    return total
```

- Assignment creates a local unless declared `global`/`nonlocal`.
- `global` writes module state (avoid; repo bans mutable globals).
- `nonlocal` writes the enclosing function (closures, decorators).
- Loops do not make scope; functions, classes, and comprehensions do.

```python
def outer() -> int:
    """Nonlocal counter."""
    count = 0

    def bump() -> int:
        nonlocal count
        count += 1
        return count

    bump()
    return count
```

Loop leak trap: `for i in ...` after the loop, `i` still exists at
function scope. Comprehensions do not leak in Python 3.

## Next

- [09-object-model-type.md](09-object-model-type.md) — everything is
  an object, `type()`, introspection.
- [04-classes-oop.md](04-classes-oop.md) — full class reference.
