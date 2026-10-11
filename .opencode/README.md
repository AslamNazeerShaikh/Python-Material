# Opencode Configuration for Python-Material

Python study + logic-building practice repo: one-folder-per-topic exercises with notes, pytest suite, runnable demos.
Model: `opencode/muse-spark-1.3-contributor-free` via OpenCode Zen (reasoning effort high).

Style authority: `docs/STYLE_GUIDE.md` (PEP 8 + Google Python Style Guide + IST best-practices gist + clean/efficient-code practices).
Every agent review and every skill example must conform to it.

## Structure

```
.opencode/
├── opencode.json              # Main configuration (model, agents, skills, commands, MCP)
├── agents/                    # Agent definitions
│   ├── python-practice-assistant.md  # Main Python coach (default)
│   ├── code-reviewer.md       # Style-guide-grounded review checklist
│   ├── test-writer.md         # pytest specialist
│   └── documentation-writer.md# Keeps README + per-topic notes in sync
├── skills/                    # Skill definitions
│   ├── python-development.md  # Idiomatic Python patterns for exercises
│   ├── testing-strategy.md    # pytest stack (pinned versions)
│   └── graphify/              # Knowledge-graph skill (untouched, shared)
├── commands/                  # Custom commands
│   ├── build.md test.md run.md clean.md lint.md format.md  # Shortcuts
│   └── python-build.md python-test.md python-run.md python-clean.md python-lint.md
├── permissions/               # Permission rules (python + graphify bash allows, destructive denies)
│   └── default.md
├── lsp/                       # pyright + JSON + Ruff
│   └── default.md
└── plugins/
    └── graphify.js            # Knowledge-graph reminder hook (untouched, shared)
```

## Repo layout (target project)

| Path | Purpose |
|---|---|
| `src/python_material/<category>/<topic>/` | One exercise per folder: `<topic>.py` + `PROBLEM.md` |
| `src/python_material/common/` | Shared helpers (e.g. enums like `SortDirection`) |
| `tests/test_<category>/test_<topic>.py` | pytest suite mirroring the package |
| `demos/` | Runnable demo scripts (only place with `print` output) |
| `docs/STYLE_GUIDE.md` | Enforceable style/formatting/best-practice rules |
| `docs/PROBLEM_TEMPLATE.md` | Template for new exercise briefs |
| `pyproject.toml` | Build config: ruff, mypy, pytest, coverage |

## Agents

| Agent | Purpose |
|-------|---------|
| `python-practice-assistant` | Main Python coach (default): new exercises, explanations, manual-before-builtin |
| `code-reviewer` | Reviews exercises against `docs/STYLE_GUIDE.md` checklist |
| `test-writer` | Adds pytest tests mirroring `src/python_material` |
| `documentation-writer` | Keeps root `README.md` + per-topic notes in sync |

## Skills

| Skill | Description |
|-------|-------------|
| `python-development` | Manual implementations, builtin comparisons, dataclasses, typing, async |
| `testing-strategy` | Pinned pytest/pytest-cov stack, `pytest` runs |

## Commands

| Command | Description |
|---------|-------------|
| `build` / `python-build` | `python -m compileall src && pip install -e .` |
| `test` / `python-test` | `pytest` (+ `-k`, `--cov`) |
| `run` / `python-run` | `python demos/main.py` |
| `clean` / `python-clean` | Remove `__pycache__`, `.pytest_cache`, coverage artifacts |
| `lint` / `python-lint` | `ruff check . && ruff format --check . && mypy src` |
| `format` | `ruff check --fix . && ruff format .` |

## Guardrails

- Bash `*` allowed, except destructive commands are denied: `rm -rf *`, `sudo *`, `chmod 777 *` (full deny list in `permissions/default.md`).
- Sensitive files (`.env*`, `*.key`, `*.pem`, `secrets.*`, `credentials.*`) are neither written nor read.
- Never install toolchains/packages on your own — give copy-pasteable commands instead.
- Every commit follows Conventional Commits (`docs/COMMIT_CONVENTION.md`); enforced by `githooks/commit-msg` (`git config core.hooksPath githooks`).

## Usage

### Switch Agent
```
> agent code-reviewer
```

### Run Command
```
> build
> test --coverage
```

### Knowledge graph
```
> /graphify
```
(`graphify update .` after code changes once `graphify-out/` exists; see `AGENTS.md`)

## Documentation

- [Opencode Config](https://opencode.ai/docs/config/)
- [Opencode Agents](https://opencode.ai/docs/agents/)
- [Opencode Models](https://opencode.ai/docs/models/) (Zen model IDs use `opencode/<model-id>`)
- [Opencode Commands](https://opencode.ai/docs/commands/)
- [Opencode Permissions](https://opencode.ai/docs/permissions/)
- [Opencode LSP](https://opencode.ai/docs/lsp/)
