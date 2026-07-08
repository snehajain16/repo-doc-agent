# How It Works

README AI Agent uses Claude's tool-use API to explore your repository like a developer would — reading files, detecting languages, parsing dependencies — then writes a README grounded in what it actually found.

## The Agent Loop

```
User invokes CLI / GitHub Action
        │
        ▼
┌─────────────────────────────────┐
│         ReadmeAgent             │
│  system prompt + tools schema   │
└────────────┬────────────────────┘
             │  messages[]
             ▼
      ┌─────────────┐
      │   Claude    │◄──────────────────┐
      │  (tool_use) │                   │
      └──────┬──────┘                   │
             │ tool_use blocks          │ tool_result blocks
             ▼                          │
      ┌─────────────┐                   │
      │ dispatch_   │                   │
      │ tool()      │───────────────────┘
      └─────────────┘
      (list_files, read_file,
       search_code, detect_language,
       read_dependency_file)

      ... up to 20 tool calls ...

             │  stop_reason = "end_turn"
             ▼
      ┌─────────────┐
      │  ReadmeData │  (Pydantic model)
      │  JSON       │
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │  Jinja2     │
      │  Renderer   │
      └──────┬──────┘
             │
             ▼
        README.md
```

## Components

### `readme_agent/agent.py` — The Brain
`ReadmeAgent` runs a `while` loop calling the Anthropic API. Each iteration either processes tool calls (passing results back as `tool_result` blocks) or returns the final `ReadmeData` JSON when Claude signals `end_turn`.

### `readme_agent/tools.py` — The Eyes
Five tools Claude can invoke to explore the repo:
| Tool | What it does |
|---|---|
| `list_files(path)` | Lists files/dirs at a path |
| `read_file(path)` | Reads file content (truncated at 8000 chars) |
| `search_code(pattern)` | Regex search across all text files |
| `detect_language()` | Infers primary language + frameworks |
| `read_dependency_file()` | Parses deps from package.json, requirements.txt, go.mod, etc. |

All tools validate paths stay inside the repo root — no traversal possible.

### `readme_agent/renderer.py` — The Voice
Takes the structured `ReadmeData` and renders it through a Jinja2 template into clean Markdown. Sections are omitted if empty, so the output never has placeholder headings.

### `readme_agent/github_writer.py` — The Hands
Uses the GitHub API (via PyGithub) to commit the generated README back to the repo. Idempotent — skips the commit if the content hasn't changed.

## Why Tool-Use Instead of Prompt Engineering?

With prompt engineering alone, you'd have to dump the entire repo into the context window, hope Claude extracts the right things, and get generic output because the model doesn't know what to look for.

With tool-use, Claude **decides** which files to read. It starts at the root, sees something interesting (a `pyproject.toml`, a `main.go`, a `src/` directory), and drills in. It only reads what's relevant, and the README reflects what it actually found.
