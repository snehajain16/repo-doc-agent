# Spec 001 — README AI Agent
> Status: Approved | Created: 2026-07-08

## Overview

An AI agent that automatically generates high-quality, accurate README files for any GitHub repository. Instead of template-filling, the agent uses Claude's tool-use API to explore a repository like a developer would — reading files, detecting languages, finding entry points — then writes a README grounded in what it actually found.

---

## Problem Statement

Developers consistently skip or delay writing READMEs because it's tedious and requires describing what they already know deeply. Existing automated tools produce generic, low-quality docs because they use regex/heuristics rather than understanding. Poor documentation slows onboarding, reduces open-source adoption, and creates maintenance burden.

---

## Goals

1. Generate READMEs that are accurate, specific, and useful — not generic boilerplate.
2. Run as a GitHub Action so it works automatically on push/PR with zero developer effort.
3. Provide a local CLI for developers who want to preview or customise the output.
4. Be fast enough for CI (< 60s for a typical repo).
5. Be deterministic enough that re-running on an unchanged repo produces the same README.

## Non-Goals

- Generating docs other than README (API docs, changelogs — future scope).
- Supporting non-GitHub VCS (GitLab, Bitbucket — future scope).
- Replacing human-written READMEs entirely; the output is a strong starting point.

---

## User Stories

### US-01: Developer runs CLI locally
> As a developer, I want to run `readme-agent generate --repo-path .` and get a README.md written to my project root, so I can review and commit it myself.

**Acceptance criteria:**
- CLI accepts `--repo-path` (default: `.`) and `--output` (default: `README.md`).
- Agent explores the repo using tool calls and generates a README in < 60s.
- If README already exists, CLI prompts for confirmation before overwriting (unless `--force`).
- Output is valid Markdown.

### US-02: GitHub Action auto-generates README on push
> As a repo maintainer, I want a GitHub Action that triggers on push to main, generates a README, and commits it back — so my docs stay up to date automatically.

**Acceptance criteria:**
- Action defined in `action.yml`, usable as `uses: snehajain16/readme-ai-agent@v1`.
- Accepts `anthropic_api_key` (required), `output_path` (default: `README.md`), `model` (default: `claude-sonnet-5`).
- Commits the README back to the branch that triggered the action.
- Action is idempotent.

### US-03: Agent understands project structure
> As a user, I want the generated README to accurately describe my project's language, framework, dependencies, and entry points — not just say "this is a Python project."

**Acceptance criteria:**
- Detects primary language and framework (e.g. "FastAPI", "React + TypeScript", "Go CLI").
- Finds and parses dependency files (`requirements.txt`, `package.json`, `go.mod`, `Cargo.toml`).
- Identifies entry points (`main.py`, `index.ts`, `cmd/`, `src/main.rs`).
- Finds and summarises existing docs (`CONTRIBUTING.md`, `LICENSE`, `docs/`).

### US-04: README has consistent, useful structure
> As a reader, I want the generated README to have a predictable structure so I can quickly find setup instructions, usage examples, and contribution guidelines.

**Acceptance criteria:**
Generated README includes these sections (populated or omitted if not applicable):
- `# Project Name` + one-line description
- `## Features` — bullet list of key capabilities
- `## Prerequisites` — what you need installed
- `## Installation` — step-by-step setup
- `## Usage` — example commands / code snippets
- `## Configuration` — env vars / config files
- `## Contributing` — how to contribute
- `## License` — license info

### US-05: Verbose mode for debugging
> As a developer, I want to see what the agent is doing (which files it reads, what tools it calls) when I run with `--verbose`, so I can understand and trust the output.

**Acceptance criteria:**
- `--verbose` flag prints each tool call and its result summary to stderr.
- Normal stdout only contains the final README (or success message).

---

## Out of Scope for v1

- Multi-language README (i18n)
- Interactive Q&A mode
- Streaming output
- README diff / update mode (update existing README rather than rewrite)
