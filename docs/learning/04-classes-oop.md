# 04 — Classes and OOP

How to declare classes, fields, methods, properties, inheritance, and
interfaces. Assumes you know C# OOP; focuses on what differs.

## 1. Minimal class

```python
class Animal:
    """Base animal."""

    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("name must not be empty")
        self.name = name  # Field created by assignment.

    def speak(self) -> str:
        """Return the animal sound."""
        return "..."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
```

1. No `new`: `a = Animal("cat")`.
2. `self` is explicit (`this` passed as first param).
   `a.speak()` equals `Animal.speak(a)`.
3. Class-level `name: str` alone stores nothing. Assignment in
   `__init__` creates the field.
4. Use `self.__class__.__name__` in `__repr__` so subclasses print
   correctly.

## 2. Method types

```python
class Point:
    """2D point with factories."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int) -> None:
        """Instance method: takes self, mutates state."""
        self.x += dx
        self.y += dy

    @classmethod
    def from_tuple(cls, value: tuple[int, int]) -> "Point":
        """Named constructor. Use cls(), not Point(), for subclass safety."""
        return cls(value[0], value[1])

    @staticmethod
    def is_origin(x: int, y: int) -> bool:
        """Stateless helper. No self/cls. Often better as a module function."""
        return x == 0 and y == 0
```

This repo prefers module-level functions over `@staticmethod`, and
`@classmethod` only for named constructors and class-state routines.

## 3. No real access modifiers

```python
self.x  # Public.
self._x  # Internal by convention. Importable, but do not touch.
self.__x  # Name-mangled to _ClassName__x. Avoids subclass clashes.
```

`obj._Cls__x` still reaches mangled names. There is no enforcement.
Validate with `@property`, do not rely on hiding.

Properties replace C# `get; set;` for cheap derivations:

```python
class Circle:
    """Circle with validated radius."""

    def __init__(self, radius: float) -> None:
        self.radius = radius  # Goes through the setter.

    @property
    def radius(self) -> float:
        """Return the radius."""
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("radius must be >= 0")
        self._radius = value
```

Use a `_radius` backing store. Assigning `self.radius` inside the
getter or setter recurses. Only use `@property` for cheap,
unsurprising reads, never for expensive work or trivial get/set
(make the attribute public instead).

## 4. Inheritance and MRO

```python
class Dog(Animal):
    """Dog specialization."""

    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)  # C# base(name).
        self.breed = breed

    def speak(self) -> str:  # Virtual + override by default.
        return "woof"
```

Python allows multiple bases. Lookup follows `Class.__mro__`:

```python
class A:
    def run(self) -> str:
        return "A"


class B(A):
    def run(self) -> str:
        return "B"


class C(A):
    def run(self) -> str:
        return "C"


class D(B, C):
    """MRO is D, B, C, A, object. D().run() is B."""
```

Inspect with `D.__mro__` or `help(D)`. Every class in a cooperative
chain should call `super().__init__()` so MRO dispatch works.

Edge: method name typos do not error; they create a new method that
never overrides. Tests catch this, the compiler does not.

## 5. Abstraction: ABC vs Protocol

Enforced base (C# `abstract class`):

```python
from abc import ABC, abstractmethod


class Speaker(ABC):
    """Must-speak base."""

    @abstractmethod
    def speak(self) -> str:
        """Return the sound."""
        raise NotImplementedError
```

`Speaker()` raises `TypeError`. Subclasses must implement `speak`.

Structural interface (C# `interface`, duck-typed):

```python
from typing import Protocol


class SpeakerP(Protocol):
    """Anything with .speak() qualifies."""

    def speak(self) -> str: ...


def loud(speaker: SpeakerP) -> str:
    """Work with any matching object, no inheritance needed."""
    return speaker.speak().upper()
```

Prefer `Protocol` for flexible APIs, `ABC` when you need shared base
logic or strict instantiation blocking.

## 6. Dataclasses, enums, slots

C# `record` equivalent without `__init__`/`__eq__`/`__repr__`
boilerplate:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PointData:
    """Immutable point value."""

    x: int
    y: int
```

Enum:

```python
from enum import Enum


class SortDirection(Enum):
    """Sort order. Never use bool flags for direction."""

    ASCENDING = "asc"
    DESCENDING = "desc"
```

`__slots__` restricts fields and saves memory:

```python
class Slim:
    """No __dict__, no dynamic attributes."""

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
```

Avoid by default. It complicates multiple inheritance and pickling.

## 7. Polymorphism, errors, resources

- Polymorphism is duck-typed. `mypy` plus `Protocol` restore C#-like
  checking. Runtime style is EAFP: `try/except AttributeError`
  narrowly, not `null` checks everywhere.
- `__eq__` without `__hash__` makes instances unhashable. Define both
  or set `__hash__ = None` intentionally. Use
  `@functools.total_ordering` when ordering.
- `with` plus `__enter__/__exit__` is C# `using`. Narrow `try`,
  specific `except`, `raise X from Y` for chaining.
- No mutable globals, no `print()` in `src/`, `datetime.now(timezone.utc)`
  only, `pathlib` for paths.

Full example tying it together:

```python
"""animals.py."""

from __future__ import annotations

__all__ = ["Animal", "Dog"]


class Animal:
    """Base animal."""

    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("name must not be empty")
        self.name = name

    def speak(self) -> str:
        """Return the sound."""
        return "..."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class Dog(Animal):
    """Dog specialization."""

    def speak(self) -> str:
        """Return the sound."""
        return "woof"


def main() -> None:
    print(Dog("rex"))


if __name__ == "__main__":
    main()
```

## Next

- [README.md](README.md) — index.
- [02-dunder-attributes.md](02-dunder-attributes.md) — object protocol.
