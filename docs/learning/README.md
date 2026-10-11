# Python Learning Hub — C# to Python

Study notes for a C# developer learning Python module, function, and class
mechanics. Each topic is one file with what/why/where/how/when plus edge
cases and C# comparisons.

| # | Topic | File | What you learn |
|---|---|---|---|
| 0 | C# → Python mental model | [00-csharp-to-python.md](00-csharp-to-python.md) | Namespaces vs modules, `using` vs `import`, types, access modifiers |
| 1 | Modules and packages | [01-modules-packages.md](01-modules-packages.md) | Files as modules, `__init__.py`, imports, scripts vs libraries |
| 2 | Dunder attributes | [02-dunder-attributes.md](02-dunder-attributes.md) | `__name__`, `__main__`, `__all__`, `__version__`, `__author__`, `__init__`, and the other popular ones |
| 3 | Functions with `def` | [03-functions-def.md](03-functions-def.md) | Params, args/kwargs, returns, hints, `lambda`, decorators, generators |
| 4 | Classes and OOP | [04-classes-oop.md](04-classes-oop.md) | `class`, `self`, methods, properties, inheritance, MRO, ABC/Protocol, dataclasses |

Conventions used in all files: `src/` layout, pure library code (return
values, no `print()`), Google-style docstrings, type hints on public
signatures, `ValueError` guards on public APIs.
