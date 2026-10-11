---
name: clean
description: Remove Python build/test artifacts (__pycache__, .pytest_cache, coverage)
category: clean
command: find . -type d -name __pycache__ -prune -exec rm -rf {} + && rm -rf .pytest_cache .coverage coverage.xml htmlcov
examples:
  - find . -type d -name __pycache__ -prune -exec rm -rf {} +
  - rm -rf .pytest_cache .coverage coverage.xml htmlcov
