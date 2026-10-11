---
name: testing-strategy
description: pytest + pytest-cov strategy for Python-Material
version: 1.0.0
author: opencode
tags:
  - testing
  - pytest
  - coverage
capabilities:
  - unit-testing
  - test-fixtures
  - coverage-analysis
references:
  - "https://docs.pytest.org/"
  - "https://pytest-cov.readthedocs.io/"
examples:
  - name: "Dev dependencies (pinned)"
    description: "Test stack from pyproject.toml [project.optional-dependencies] dev"
    code: |
      pytest==8.3.4
      pytest-cov==6.0.0
      ruff==0.9.4
      mypy==1.14.1

  - name: "Exercise test with edge cases"
    description: "One test module per topic; edge cases first, parametrize, test_when naming"
    code: |
      """Tests for unique character counting."""
      import pytest

      from python_material.strings.unique_char_counter import count_unique


      @pytest.mark.parametrize(
          ("value", "expected"),
          [("", 0), ("a", 1), ("hello", 4)],
      )
      def test_counts_unique_chars_when_given_words(value: str, expected: int) -> None:
          assert count_unique(value) == expected

  - name: "Fixture for generated inputs"
    description: "tmp_path / monkeypatch for I/O-shaped exercises"
    code: |
      """Fixture example."""

      def test_reads_words_when_file_exists(tmp_path) -> None:
          target = tmp_path / "words.txt"
          target.write_text("alpha\nbeta\n", encoding="utf-8")
          assert target.read_text(encoding="utf-8").split() == ["alpha", "beta"]

  - name: "Run + coverage"
    description: "pytest with the coverage gate from pyproject.toml"
    code: |
      pytest
      pytest --cov=src --cov-report=term-missing
      pytest tests/test_strings -k unique
