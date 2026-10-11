# Python-Material

Study + logic-building practice repo: manual implementation first, then the builtin/stdlib version.

Style authority: [`docs/STYLE_GUIDE.md`](docs/STYLE_GUIDE.md) (PEP 8 + Google Python Style Guide + IST best-practices gist + clean/efficient-code practices). All code and all AI reviews conform to it.

## Layout

```text
src/python_material/arrays/<topic>/... + PROBLEM.md
src/python_material/strings/<topic>/... + PROBLEM.md
src/python_material/common/          # shared helpers like SortDirection
tests/test_arrays|test_strings/test_<topic>.py
demos/main.py                        # demo runner, only place with print() output
docs/STYLE_GUIDE.md                  # enforceable style/formatting/best-practice rules
docs/PROBLEM_TEMPLATE.md
```

New exercise: copy `docs/PROBLEM_TEMPLATE.md` to
`src/python_material/<category>/<topic>/PROBLEM.md`, add pure functions to the
package (return values, no `print()`), add tests + a demo entry.

## Index

| Problem | Category | Technique | Complexity |
|---|---|---|---|
| SecondLargestNumber | Arrays | single pass / `sorted(set())` | O(n) / O(n log n) |
| CustomSorter | Arrays | bubble sort vs builtin sort | O(n²) / O(n log n) |
| VowelCounter | Strings | manual scan vs set comprehension | O(n) |

## Question Bank

Scenario-based interview Q&A with answers and explanations: [`docs/question-bank/`](docs/question-bank/) (seeded per topic as exercises land).

## Commands

- `pip install -e ".[dev]"` (once; prefer a venv: `python -m venv .venv`)
- `pytest` / `pytest --cov=src --cov-report=term-missing`
- `python demos/main.py`
- `ruff check --fix . && ruff format . && mypy src`

## Practice strategies

- Improve your logic-building skills and gain confidence in solving tricky Python questions, try the following strategies:

## 1. Practice Basics Without Builtin Helpers 🛠️🐸

Write code for basic operations without using builtin helpers to understand the underlying logic. Examples:

- Implement methods for common string manipulations like reversing a string, finding substrings, or checking for palindromes.
- Build custom implementations for list operations (e.g., adding, removing, finding elements).

## 2. Nested Loops and Arrays 🍃🔄

Nested for loops are frequently used for multidimensional arrays or matrices. Try problems involving:

- Matrix transposition and rotation.
- Summing diagonals, rows, or columns in a 2D array.
- Implementing your own sorting algorithms like Bubble Sort or Selection Sort on lists without using `sorted()`.

## 3. String and Character Manipulations 🔠📜

String problems often test logic with character-by-character manipulations. Practice tasks such as:

- Counting specific characters or substrings.
- Removing duplicates or rearranging characters.
- Converting between character cases and implementing your own `lower()` or `upper()`.

## 4. Master Basic Data Structures 📊📅

Collections like `list`, `dict`, `set`, and `tuple` are crucial in problem-solving:

- Write your own versions of `append` and `remove` for a dynamic array structure.
- Implement a simple key-value store like a `dict` without using builtin dict classes.
- Practice data retrieval operations like searching for values or keys in a dictionary.

## 5. Explore Code Challenges 🧩🪛

Platforms like LeetCode, HackerRank, and Codewars offer problems categorized by topic (e.g., arrays, strings, data structures). These will help reinforce Python skills while building up speed and logic. Choose problems rated "easy" or "medium" to get comfortable before advancing to harder problems.

## 6. Read and Write Code Regularly 📚✍️

Find and read solutions to common algorithmic problems in Python to see different approaches. Then, try writing your own code based on what you learned without copying directly.
