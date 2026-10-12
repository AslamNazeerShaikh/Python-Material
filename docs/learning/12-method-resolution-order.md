# 12 — Method Resolution Order (MRO)

Which method runs when several bases define it, why that one wins,
what breaks the chain, and the practices that keep hierarchies sane.
Assumes `04` (classes) and `04` §9 (`super()`); focuses on the lookup
machinery underneath.

## 1. What and why

One rule: attribute lookup on an instance walks
`type(obj).__mro__` — a tuple of classes in winner-first order — and
uses the first match. Single inheritance makes the tuple obvious
(`Kid, Base, object`). Multiple inheritance needs a deterministic
merge, so Python linearizes every hierarchy with the **C3
algorithm**: children precede parents, left bases precede right
bases, and no class appears before an ancestor of another base
(monotonicity). The result is computed once at `class` time and
stored as `Cls.__mro__`.

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

## 2. Reading the MRO

```python
D.__mro__  # (D, B, C, A, object). Tuple: the official order.
D.mro()  # [D, B, C, A, object]. Same order as a fresh list.
[type(c).__name__ for c in D.__mro__]  # Names for humans/logs.
help(D)  # Human-readable: MRO section plus method list.
```

`__mro__` is a tuple (immutable, canonical); `mro()` returns a new
list (mutable copy for inspection). `object` is always last — every
class derives from it, even when unwritten.

## 3. C3 by hand (and why depth-first intuition fails)

Naive depth-first would read `D(B, C)` as D, B, A, C — A before C.
C3 refuses: C also derives from A, so A must follow C. Merge the
base linearizations left to right, taking a head only if it appears
in no other tail:

1. L(B) = B, A, object; L(C) = C, A, object; bases = B, C.
2. Take B (in no tail). Then C (in no remaining tail).
3. Then A, then object. Final: D, B, C, A, object.

Memorize the shape, not the algorithm: **left wins, children first,
shared ancestors sink below every child that needs them.**

## 4. `super()` rides the MRO, and cooperation keeps it moving

Zero-arg `super()` means "continue lookup after the current class in
this instance's MRO". The cooperative diamond runs each link once:

```python
calls: list[str] = []


class Top:
    def __init__(self) -> None:
        calls.append("Top")


class Left(Top):
    def __init__(self) -> None:
        calls.append("Left")
        super().__init__()


class Right(Top):
    def __init__(self) -> None:
        calls.append("Right")
        super().__init__()


class Bottom(Left, Right):
    def __init__(self) -> None:
        calls.append("Bottom")
        super().__init__()


Bottom()  # calls is ["Bottom", "Left", "Right", "Top"]. Top once.
```

Constructors with different parameters cooperate through keyword
forwarding — each link takes what it owns and passes the rest on:

```python
class Named:
    def __init__(self, name: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.name = name


class Aged:
    def __init__(self, age: int, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.age = age


class Person(Named, Aged):
    def __init__(self, name: str, age: int) -> None:
        super().__init__(name=name, age=age)
```

## 5. C# vs Python: resolution machinery

| C# | Python | Same? |
|---|---|---|
| Single class base plus interfaces (compiler-fixed, one chain) | Any number of bases merged by C3 into `__mro__` | Different — Python computes an order, C# declares one |
| Diamond via interfaces: each interface keeps its own slot; explicit implementation (`void ILeft.Run()`) disambiguates | Diamond via classes: first MRO match wins; `super()` continues the same chain | Different — slots vs single ordered chain |
| `base(...)` always means the lexical parent | `super()` means "next in this instance's MRO" (mixin, not parent) | Different — dynamic start point |
| `virtual` / `override` keywords; missing `override` warns | Virtual-by-default; a typo silently creates a new method | Different — no keyword, no check |
| `sealed` stops further overriding (enforced) | `@typing.final` is checker-only; MRO never blocks | Different — advisory only |
| Ambiguity fails at compile time with a named error | Conflicting bases fail at `class` time: `TypeError: Cannot create a consistent method resolution order` | Similar outcome (fail-fast), different moment |

## 6. Edge cases (all verified by execution)

1. Conflicting precedence is `TypeError` at class creation:
   `AB(A, B)` plus `BA(B, A)` under one `X(AB, BA)` cannot order A
   vs B. The exact message names the bases. Fix by reordering one
   pair, not by patching at runtime.
2. A link that skips `super().__init__()` truncates the chain:
   everything after it in the MRO never runs. Missing attributes
   then surface far away as `AttributeError` (see `04` §8e).
3. Explicit parent calls double-initialize diamonds: `L.__init__`
   plus `R.__init__` each calling `T.__init__` runs Top twice
   (`["D", "L", "T", "R", "T"]`). One `super().__init__()` per link
   is the whole fix.
4. Mixin order decides the winner: `C(M1, M2)` answers `M1.who`,
   `C(M2, M1)` answers `M2.who`. Put mixins (behaviour add-ons)
   before concrete bases, most specific first.
5. `super()` needs a method context. Zero-arg `super()` in a
   `@staticmethod` is `RuntimeError` (no instance/class to anchor
   to); in a `@classmethod` it works (`cls` anchors it, staying
   subclass-aware).
6. `Cls.__mro__` is a tuple, `Cls.mro()` a list. Mutating the list
   changes nothing; reassigning `Cls.__bases__` recomputes the MRO
   (and can raise the `TypeError` from edge 1). Rare, test-covered
   metaprogramming only.
7. Method-name typos (`def speek`) create silent new methods that
   never enter the intended MRO slot. Tests own override checking;
   the interpreter never will.

## 7. Best practices

1. Every `__init__` (and every overriding method that extends)
   calls `super().__init__()` exactly once, first — no exceptions,
   even in single inheritance (future mixins reuse the chain).
2. Mismatched constructor signatures cooperate via `**kwargs`
   forwarding (§4); never call grandparents or siblings explicitly.
3. Order bases most-specific-first, mixins before concrete classes;
   read the winner back with `Cls.__mro__` after writing it.
4. Keep hierarchies shallow (two to three levels). Depth plus
   breadth is where C3 surprises live; composition or `Protocol`
   covers most "reusable behaviour" needs without any MRO at all.
5. Never use `__bases__` surgery, `__mro__` patching, or metaclasses
   as architecture (repo ban on power features, `STYLE_GUIDE`
   §10.4). If the MRO needs patching, the design needs flattening.
6. Assert the order in tests for load-bearing diamonds:
   `[c.__name__ for c in Bottom.__mro__]` plus a call-trace list
   like `calls` in §4 pins the chain against refactors.

## Next

- [README.md](README.md) — index.
- [04-classes-oop.md](04-classes-oop.md) — class reference (`super()`
  deep-dive in §9, constructor matrix in §8).
- [09-object-model-type.md](09-object-model-type.md) — identity,
  `type()`, pillars.
- [11-access-modifiers-and-shared-mutation.md](11-access-modifiers-and-shared-mutation.md) —
  class-vs-instance state on the shared chain.
