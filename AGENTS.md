# Python-Material — agent instructions

Python study + logic-building practice repo. Package `src/python_material/`: `common/` (shared helpers like `SortDirection`) + per-category exercise folders (each with implementation `.py` + `PROBLEM.md`); `tests/` (pytest, mirrors package); `demos/` (demo runner, only place with `print()` output).

## Toolchain

- Python 3.14, src layout, `pip install -e ".[dev]"` (prefer a venv: `python -m venv .venv`).
- `pytest` / `pytest --cov=src --cov-report=term-missing`; demos with `python demos/main.py`.
- Gates: `ruff check .`, `ruff format --check .`, `mypy src` — all green before commit.
- Style authority is `docs/STYLE_GUIDE.md` (PEP 8 + Google pyguide + IST gist + clean-code practices); every review cites its section.
- Full agent/skill/command inventory lives in `.opencode/README.md`; config in `.opencode/opencode.json`.

## Conventions

- New exercise = `src/python_material/<Category>/<topic>/` (`arrays`, `strings`, ...) with implementation `.py` + `PROBLEM.md` (copy `docs/PROBLEM_TEMPLATE.md`), plus tests in `tests/test_<category>/test_<topic>.py` and a demo entry in `demos/main.py`.
- Library is pure: return values, no `print()`, no `input()`; `ValueError` guards on public APIs (never bare `except:`).
- Interview Q&A bank lives in `docs/question-bank/` (one file per topic, questions + answers + explanations); link new bank files from `docs/question-bank/README.md`.
- Practice-first: manual implementation (`find_second_largest`) before the builtin shortcut (`find_second_largest_builtin`); keep both where instructive.
- Use `SortDirection` enum (`python_material.common`), never `bool` direction flags; use `"".join()` instead of `str +=` in loops.
- Google-style docstrings on all public modules/functions/classes; type hints on all public signatures; UTC-aware timestamps (`datetime.now(timezone.utc)`, never naive `datetime.now()`).
- Never install toolchains, packages, or tools automatically — give copy-pasteable commands instead.

## Guardrails

- Destructive bash is denied (`rm -rf *`, `sudo *`, `chmod 777 *`, force-push, `curl * | bash` — full list in `.opencode/permissions/default.md`).
- Never read or write secrets (`.env*`, `*.key`, `*.pem`, `secrets.*`, `credentials.*`).

## Commits

- Every commit MUST follow Conventional Commits per `docs/COMMIT_CONVENTION.md`:
  `<type>[optional scope][optional !]: <description>` (types: `feat`, `fix`,
  `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`).
- One commit = one type; split mixed changes. Agents writing commits obey the
  same rule — no exceptions.
- The `commit-msg` hook enforces this; enable with `git config core.hooksPath githooks`.

## graphify

This project uses the shared graphify skill (`.opencode/skills/graphify/`) and reminder plugin (`.opencode/plugins/graphify.js`).

Rules (apply once `graphify-out/graph.json` exists):

- For codebase questions, first run `graphify query "<question>"`. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts.
- If `graphify-out/wiki/index.md` exists, use it for broad navigation instead of raw source browsing.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
