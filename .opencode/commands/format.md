---
name: format
description: Auto-fix and format Python-Material code (ruff)
category: quality
command: ruff check --fix . && ruff format .
examples:
  - ruff check --fix .
  - ruff format .
  - ruff format --check .
