# Contributing

## Setup

```bash
git clone https://github.com/snehajain16/repo-doc-agent
cd repo-doc-agent
uv sync --dev
```

## Running Tests

```bash
uv run pytest
uv run ruff check .
uv run mypy readme_agent/
```

## Testing the GitHub Action locally

Install [act](https://github.com/nektos/act) then:

```bash
act push -s ANTHROPIC_API_KEY=your_key_here
```

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Specs, constitution, stable code |
| `feature/*` | One feature per branch, merged via PR |

## Submitting Changes

1. Branch from `main`
2. Make changes with tests
3. Open a pull request
