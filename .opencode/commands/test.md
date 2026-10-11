---
name: test
description: Run pytest suite for Python-Material (pytest + pytest-cov)
category: test
command: pytest
args:
  - name: path
    description: Test path to run
    type: string
    default: tests
  - name: filter
    description: Keyword filter expression (-k)
    type: string
    default: ""
  - name: coverage
    description: Collect coverage with term-missing report
    type: boolean
    default: false
examples:
  - pytest
  - pytest tests/test_arrays -k second_largest
  - pytest --cov=src --cov-report=term-missing
