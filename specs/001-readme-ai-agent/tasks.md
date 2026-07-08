# Tasks 001 — README AI Agent
> Status: Ready | Created: 2026-07-08

Tasks are dependency-ordered. Each maps to a feature branch. Complete T-01 before T-02, etc. within each branch.

---

## T-01 · Project Scaffold
**Branch:** `feature/agent-core`
**Depends on:** nothing

- [ ] Initialise `pyproject.toml` with `uv` (`name`, `version`, `dependencies`, `scripts`)
- [ ] Add runtime deps: `anthropic`, `click`, `rich`, `jinja2`, `pydantic`, `PyGithub`
- [ ] Add dev deps: `pytest`, `pytest-mock`, `ruff`, `mypy`
- [ ] Create `readme_agent/__init__.py` with version constant
- [ ] Create `.github/workflows/ci.yml` — runs `pytest` + `ruff` + `mypy` on push
- [ ] Add `.gitignore` for Python

**Done when:** `uv run pytest` exits 0 (no tests yet, just collection passes).

---

## T-02 · Agent Core Loop
**Branch:** `feature/agent-core`
**Depends on:** T-01

- [ ] Create `readme_agent/agent.py` with `ReadmeAgent` class
- [ ] Implement `generate(repo_path: Path) -> ReadmeData` method
- [ ] Write system prompt with tool list, README structure, accuracy instructions
- [ ] Implement tool-use `while` loop using `anthropic` SDK
- [ ] Handle `max_tool_calls=20` safety limit
- [ ] Parse Claude's final JSON response into `ReadmeData`
- [ ] Unit test: mock Anthropic client, assert loop terminates and returns `ReadmeData`

**Done when:** unit test passes with mocked Claude responses.

---

## T-03 · Repo Explorer Tools
**Branch:** `feature/repo-explorer`
**Depends on:** T-01

- [ ] Create `readme_agent/tools.py`
- [ ] Implement `list_files(path, repo_root) -> list[str]` with path-traversal guard
- [ ] Implement `read_file(path, repo_root) -> str` — truncate at 8000 chars, guard path
- [ ] Implement `search_code(pattern, repo_root) -> list[dict]` using `re` / `pathlib`
- [ ] Implement `detect_language(repo_root) -> dict` — count extensions, detect frameworks
- [ ] Implement `read_dependency_file(repo_root) -> dict` — parse `requirements.txt`, `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`
- [ ] Unit tests for each tool including path-traversal rejection

**Done when:** all tool unit tests pass.

---

## T-04 · Tool Registry (connect T-02 and T-03)
**Branch:** `feature/repo-explorer`
**Depends on:** T-02, T-03

- [x] Create `TOOLS_SCHEMA` list (Anthropic tool definitions) in `tools.py`
- [x] Create `dispatch_tool(name, args, repo_root) -> str` function
- [x] Wire `dispatch_tool` into `ReadmeAgent.generate()` loop
- [x] Integration test: run agent against `tests/fixtures/python-fastapi/` fixture, assert `ReadmeData.project_name` is correct

**Done when:** integration test passes with mocked Claude but real tools.

---

## T-05 · Data Models
**Branch:** `feature/readme-renderer`
**Depends on:** T-01

- [ ] Create `readme_agent/models.py`
- [ ] Define `ReadmeData`, `UsageExample`, `ConfigItem`, `Badge` Pydantic models
- [ ] Add `model_validate` tests for valid and invalid data

**Done when:** model tests pass.

---

## T-06 · README Renderer
**Branch:** `feature/readme-renderer`
**Depends on:** T-05

- [ ] Create `templates/readme.md.j2` Jinja2 template covering all README sections
- [ ] Create `readme_agent/renderer.py` with `render(data: ReadmeData) -> str`
- [ ] Handle optional sections (omit if `None` or empty list)
- [ ] Unit test: render a known `ReadmeData` fixture, assert key strings present
- [ ] Snapshot test: rendered output matches `tests/snapshots/python-fastapi-readme.md`

**Done when:** renderer tests pass.

---

## T-07 · CLI
**Branch:** `feature/cli`
**Depends on:** T-02, T-06

- [x] Create `readme_agent/cli.py` with `click` group and `generate` command
- [x] Flags: `--repo-path` (default `.`), `--output` (default `README.md`), `--model`, `--verbose`, `--force`, `--json`
- [x] `--verbose` wires `rich` logging of each tool call to stderr
- [x] Prompt for confirmation if output file exists and `--force` not set
- [x] `--json` prints `ReadmeData` as JSON to stdout instead of writing file
- [x] CLI integration test: invoke via `click.testing.CliRunner` against fixture repo

**Done when:** CLI integration test passes.

---

## T-08 · GitHub Writer
**Branch:** `feature/github-action`
**Depends on:** T-06

- [x] Create `readme_agent/github_writer.py`
- [x] Implement `commit_readme(content: str, repo: str, path: str, token: str, branch: str)`
- [x] Uses `PyGithub` to create or update file via GitHub API
- [x] Skips commit if content is identical to existing file (idempotency)
- [x] Unit test with mocked `PyGithub`

**Done when:** unit test passes, idempotency case covered.

---

## T-09 · GitHub Action
**Branch:** `feature/github-action`
**Depends on:** T-07, T-08

- [x] Create `action.yml` with inputs: `anthropic_api_key` (required), `output_path`, `model`, `commit_message`
- [x] Action runs `readme-agent generate` and calls `github_writer.commit_readme`
- [x] Create `Dockerfile` for the action (python:3.11-slim base)
- [x] Test action locally using `act` (document in `CONTRIBUTING.md`)
- [x] Add workflow `examples/demo.yml` showing how to use the action

**Done when:** `action.yml` is valid, Dockerfile builds, demo workflow exists.

---

## T-10 · Test Suite & CI
**Branch:** `feature/tests`
**Depends on:** T-01 through T-09

- [ ] Create fixture repos in `tests/fixtures/`: `python-fastapi/`, `node-react/`, `go-cli/`
- [ ] Full integration test for each fixture: mock Claude, run full pipeline, assert README sections
- [ ] Add `pytest-cov` and enforce 80% coverage gate in CI
- [ ] Add `ruff` lint check to CI
- [ ] Add `mypy` type check to CI
- [ ] Document test-running instructions in `CONTRIBUTING.md`

**Done when:** CI passes on all three fixture repos.

---

## T-11 · Dogfood & Polish
**Branch:** `main` (direct — documentation only)
**Depends on:** all above merged

- [ ] Run `readme-agent generate` on this repo itself — commit the output as `README.md`
- [ ] Write `CONTRIBUTING.md`
- [ ] Write `docs/how-it-works.md` explaining the agent loop with a diagram
- [ ] Tag `v1.0.0`

**Done when:** repo has a README generated by itself, CONTRIBUTING.md exists, v1.0.0 tag created.
