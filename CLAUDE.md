# readme-ai-agent — Agent Context

## What this project is

An AI agent that generates README files for GitHub repositories using Claude's tool-use API. The agent explores a repo (reads files, detects languages, finds entry points) and produces a structured, accurate README — not generic boilerplate.

## Before you start any task

1. Read `.specify/memory/constitution.md` — these are non-negotiable principles.
2. Check `specs/001-readme-ai-agent/tasks.md` for the current task list and dependencies.
3. Check which feature branch you are on — never commit feature code to `main`.

## Project structure

```
readme_agent/       # Core Python package
  agent.py          # Claude tool-use loop
  tools.py          # Tool implementations (read_file, list_files, etc.)
  models.py         # Pydantic output models
  renderer.py       # Jinja2 README renderer
  cli.py            # Click CLI
  github_writer.py  # GitHub API commit-back

templates/          # Jinja2 templates
tests/              # pytest suite + fixtures
specs/              # Spec Kit specs, plans, tasks
.specify/           # Spec Kit memory and templates
action.yml          # GitHub Action definition
```

## Key constraints (from constitution)

- Agent core MUST use Claude tool-use API — no hard-coded extraction.
- All `read_file` / `list_files` calls MUST validate path stays inside repo root.
- API keys MUST only come from environment variables.
- Every behavioral change MUST have a test.
- Runtime deps: `anthropic`, `click`, `rich`, `jinja2`, `pydantic`, `PyGithub` only.

## Commands

```bash
uv run readme-agent generate --repo-path . --verbose   # generate README locally
uv run pytest                                           # run tests
uv run ruff check .                                     # lint
uv run mypy readme_agent/                               # type check
```

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Specs, constitution, docs only |
| `feature/agent-core` | T-01, T-02 |
| `feature/repo-explorer` | T-03, T-04 |
| `feature/readme-renderer` | T-05, T-06 |
| `feature/cli` | T-07 |
| `feature/github-action` | T-08, T-09 |
| `feature/tests` | T-10 |
