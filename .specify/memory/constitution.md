# Constitution — readme-ai-agent
> Version: 1.0.0 | Ratified: 2026-07-08

This document establishes the non-negotiable governing principles for the `readme-ai-agent` project. All contributors and AI coding agents MUST follow these principles. Amendments require explicit ratification and an updated version number.

---

## Principle I: Agent-First Architecture

This project is an **AI agent**, not a template renderer. The core logic MUST use Claude's tool-use API so the model itself decides which files to read, what to extract, and how to structure the README. Hard-coded extraction logic is prohibited in the agent core. Jinja2 or string templates may only be used for the final rendering step.

## Principle II: Test-Backed Change (NON-NEGOTIABLE)

Every behavioral change MUST be accompanied by automated tests. The test suite is a hard gate — CI must pass before any merge.

- Unit tests cover each tool function (file reader, language detector, dependency parser).
- Integration tests run the full agent loop against fixture repos.
- Network calls to the Anthropic API MUST be mocked in tests.
- GitHub API calls MUST be mocked in tests.

## Principle III: Single Responsibility for Tools

Each tool provided to the Claude agent MUST do exactly one thing. Tools are:
- `list_files(path)` — list files/dirs at a path
- `read_file(path)` — read a file's content
- `search_code(pattern)` — grep for a pattern
- `detect_language()` — infer primary language from file extensions
- `read_dependency_file()` — parse deps from package.json / requirements.txt / etc.

No tool may call another tool internally. The agent orchestrates; tools execute.

## Principle IV: Offline-First & Minimal Dependencies

- The CLI MUST work without internet access for repo exploration (only the Anthropic API call requires network).
- Runtime dependencies are kept intentionally lean: `anthropic`, `click`, `rich`, `jinja2`.
- No LangChain, no heavy frameworks. Direct Anthropic SDK tool-use only.

## Principle V: Security & Safe File Operations

- All file reads MUST be confined to the target repository root. Path traversal (e.g. `../../etc/passwd`) MUST be rejected.
- GitHub tokens and Anthropic API keys MUST only be read from environment variables — never hardcoded, never logged.
- The agent MUST NOT write any file except the output README (and only to the path specified by the user/action).

## Principle VI: CLI & UX Consistency

- CLI uses `click` with consistent flags: `--repo-path`, `--output`, `--model`, `--verbose`.
- All terminal output uses `rich` for formatting.
- Destructive actions (overwriting an existing README) require `--force` or prompt confirmation.
- JSON output mode available via `--json` for programmatic use.

## Principle VII: GitHub Action Compatibility

- The GitHub Action MUST be self-contained in `action.yml`.
- It MUST accept `anthropic_api_key` as a required secret input.
- It MUST commit the generated README back to the repo using the GitHub API (no shell `git` required in the action runner).
- It MUST be idempotent — running it twice produces the same output if the repo hasn't changed.

---

## Governance

- The project owner (`snehajain16`) is the ratifying authority.
- Any AI agent implementing features MUST read this constitution before starting.
- Compliance is reviewed on each PR merge.
