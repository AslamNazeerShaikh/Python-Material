---
name: python-development
description: Modern Python development practices for study + class-library-style exercises (manual-first, builtin comparisons)
version: 1.0.0
author: opencode
tags:
  - python
  - stdlib
  - typing
  - async
  - algorithms
capabilities:
  - idiomatic-python
  - manual-before-builtin
  - dataclasses
  - async-patterns
  - type-hints
  - pytest-ready
references:
  - "https://peps.python.org/pep-0008/"
  - "https://google.github.io/styleguide/pyguide.html"
  - "https://gist.github.com/ruimaranhao/4e18cbe3dad6f68040c32ed6709090a3"
examples:
  - name: "Manual string reverse (no built-ins)"
    description: "Practice-first implementation using index swaps, as in strings exercises"
    code: |
      """Manual string reversal without reversed()/slicing shortcuts."""

      def reverse(value: str) -> str:
          """Return value reversed using an explicit two-pointer scan.

          Args:
              value: The string to reverse.

          Returns:
              The reversed string.
          """
          if value is None:
              raise ValueError("value must not be None")
          chars = list(value)
          left, right = 0, len(chars) - 1
          while left < right:
              chars[left], chars[right] = chars[right], chars[left]
              left += 1
              right -= 1
          return "".join(chars)

  - name: "Builtin comparison next to the manual version"
    description: "Keep both files where instructive, mirroring <topic>.py + <topic>_builtin.py"
    code: |
      """Builtin equivalent kept beside the manual implementation."""

      def reverse_builtin(value: str) -> str:
          """Return value reversed using the standard library.

          Args:
              value: The string to reverse.

          Returns:
              The reversed string.
          """
          if value is None:
              raise ValueError("value must not be None")
          return "".join(reversed(value))

  - name: "Second largest in one pass"
    description: "O(n) single scan tracking largest and second largest; handles duplicates"
    code: |
      """Single-pass second-largest-distinct finder."""

      def find_second_largest(numbers: list[int]) -> int:
          """Return the second largest distinct value in one pass.

          Args:
              numbers: Input values (at least two distinct required).

          Returns:
              The second largest distinct value.

          Raises:
              ValueError: If fewer than two distinct values exist.
          """
          if numbers is None:
              raise ValueError("numbers must not be None")
          largest: int | None = None
          second: int | None = None
          for n in numbers:
              if n == largest:
                  continue
              if largest is None or n > largest:
                  second, largest = largest, n
              elif second is None or n > second:
                  second = n
          if second is None:
              raise ValueError("Need at least two distinct values.")
          return second

  - name: "Dataclass with pure function"
    description: "Immutable models plus total ordering for classification exercises"
    code: |
      """Exercise result model."""

      from dataclasses import dataclass

      @dataclass(frozen=True)
      class ExerciseResult:
          """Result carrying the topic name and complexity."""

          topic: str
          complexity: str
          passed: bool


      def grade(result: ExerciseResult) -> str:
          """Grade an exercise result.

          Args:
              result: The result to grade.

          Returns:
              A human-readable grade line.
          """
          if result is None:
              raise ValueError("result must not be None")
          if not result.passed:
              return f"Retry: {result.topic}"
          if result.complexity == "O(1)":
              return f"Optimal: {result.topic}"
          return f"Done: {result.topic} ({result.complexity})"

  - name: "Async demo entry point"
    description: "Async main with timeout for I/O-bound demos in demos/"
    code: |
      """Async demo with a timeout."""

      import asyncio

      async def count_unique_vowels(word: str) -> int:
          """Count unique vowels in word.

          Args:
              word: Input word.

          Returns:
              Number of distinct vowels.
          """
          await asyncio.sleep(0)
          return len({c for c in word.lower() if c in "aeiou"})


      async def main() -> None:
          """Run the demo with a 30s timeout."""
          count = await asyncio.wait_for(count_unique_vowels("Minneapolis"), 30)
          print(f"Unique vowels: {count}")


      if __name__ == "__main__":
          asyncio.run(main())
