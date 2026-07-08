# repo-doc-agent

An AI agent that generates accurate, specific README files for GitHub repositories using Claude's tool-use API.

Instead of template-filling or regex extraction, the agent explores your repo like a developer would — reading files, detecting languages, parsing dependencies — then writes a README grounded in what it actually found.

## Features

- **Agent-driven exploration** — Claude decides which files to read using tool calls; no hardcoded extraction logic
- **Language & framework detection** — identifies Python/FastAPI, TypeScript/React, Go, Rust, and more from file extensions and dependency files
- **Dependency parsing** — reads `requirements.txt`, `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`
- **Structured output** — Pydantic-validated `ReadmeData` model rendered via Jinja2 template
- **Idempotent GitHub Action** — commits README back via GitHub API, skips commit if content unchanged
- **Local CLI** — run locally with `--verbose` to see every tool call the agent makes

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Anthropic API key (`ANTHROPIC_API_KEY`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/snehajain16/repo-doc-agent
   cd repo-doc-agent
   ```
2. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

Generate a README for any local repository:

```bash
export ANTHROPIC_API_KEY=your_key_here
uv run readme-agent generate --repo-path /path/to/your/repo
```

Preview the structured data as JSON without writing a file:

```bash
uv run readme-agent generate --repo-path . --json
```

Watch the agent's tool calls in real time:

```bash
uv run readme-agent generate --repo-path . --verbose
```

## GitHub Action

Add this to `.github/workflows/readme.yml` in any repository:

```yaml
name: Generate README
on:
  push:
    branches: [main]

jobs:
  readme:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: snehajain16/repo-doc-agent@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Configuration

| Input | Description | Default |
|---|---|---|
| `anthropic_api_key` | Anthropic API key (required) | — |
| `output_path` | Path to write the README | `README.md` |
| `model` | Claude model to use | `claude-sonnet-5` |
| `commit_message` | Commit message for the update | `docs: update README via readme-ai-agent` |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
