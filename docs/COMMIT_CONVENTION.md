# Commit Convention — Conventional Commits (enforceable)

**Status: enforceable.** Every commit in this repo MUST follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
with the type set from the
[semantic-commit-messages gist](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716).
Agents writing commits on behalf of the user MUST produce conforming messages.

## Format

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

- `type`: one of the table below, lowercase.
- `scope` (optional): noun naming the affected area, in parentheses —
  use repo paths/areas: `arrays`, `strings`, `common`, `tests`, `demos`,
  `docs`, `opencode`, `deps`, `style-guide`, `readme`.
  E.g. `feat(arrays): add sliding-window exercise`.
- `!` before the colon marks a **breaking change** (also add a
  `BREAKING CHANGE:` footer describing it).
- `description`: short summary, present tense, lowercase first word, no
  trailing period. E.g. `add hat wobble`, not `added hat wobble.`.
- `body` (optional): blank line, then free-form paragraphs explaining
  *why*, not *what*.
- `footer(s)` (optional): blank line, then `Token: value` trailers
  (`Refs: #123`, `Reviewed-by: Z`) or `BREAKING CHANGE: <description>`.

## Types (metric: one commit, one type)

| Type | Meaning | SemVer | Example |
|---|---|---|---|
| `feat` | New feature/exercise for the user | MINOR | `feat(strings): add palindrome exercise` |
| `fix` | Bug fix | PATCH | `fix(arrays): handle all-duplicate input` |
| `docs` | Documentation only | — | `docs: correct spelling of CHANGELOG` |
| `style` | Formatting, no production code change | — | `style: run ruff format on demos` |
| `refactor` | Code change, neither feat nor fix | — | `refactor(common): rename direction helper` |
| `perf` | Performance improvement | — | `perf(arrays): single-pass second largest` |
| `test` | Add/refactor tests, no production change | — | `test(strings): cover empty-word edge case` |
| `build` | Build system, deps, `pyproject.toml` | — | `build(deps): bump pytest to 8.3.5` |
| `ci` | CI config/scripts | — | `ci: add ruff gate to workflow` |
| `chore` | Routine tasks (tooling, config, cleanup) | — | `chore(opencode): add commit-lint command` |
| `revert` | Revert a prior commit (+ `Refs:` footer with SHA) | — | `revert: let us never again speak of the noodle incident` |

## Rules

1. One commit = one type. Mixed change? Split it (`fix:` + `feat:` + `chore:`),
   never `feat+fix:`.
2. `feat`/`fix` are for user-facing behavior — not build scripts or tooling
   (those are `build:`/`chore:`).
3. Breaking changes MUST carry `!` and/or a `BREAKING CHANGE:` footer
   (→ MAJOR). All other extra types have no SemVer effect.
4. Merge commits (`Merge ...`) and `... into ...` messages bypass the lint.
5. Human and agent commits follow the same rule — no exceptions.

## Enforcement

A `commit-msg` hook validates every message against:

```text
^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\([a-zA-Z0-9_.-]+\))?(!)?:[[:space:]].*$
```

(`[[:space:]]` — POSIX class — instead of `\s`, so the hook also works on
macOS `/bin/bash`. Same rule applies to any local port of the pattern.)

Enable it (one-time per clone — hooks don't transfer via git):

```bash
git config core.hooksPath githooks
```

The hook lives at `githooks/commit-msg` (adapted from the gist thread, CC0).
Non-conforming messages are rejected with the type table and examples.

## Changelog

| Date (UTC) | Change | Source |
|---|---|---|
| 2026-10-11 | Initial convention: CC 1.0.0 format + semantic types + hook | conventionalcommits.org v1.0.0; gist `6f47e86d2510bce28f8e7f42ae84c716` |
