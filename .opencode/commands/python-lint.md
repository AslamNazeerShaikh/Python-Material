---
name: python-lint
description: Lint + typecheck Python-Material (ruff check, ruff format check, mypy)
category: quality
command: ruff check . && ruff format --check . && mypy src
examples:
  - ruff check .
  - ruff format --check .
  - mypy src
