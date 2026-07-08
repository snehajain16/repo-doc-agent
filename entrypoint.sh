#!/bin/bash
set -e

export ANTHROPIC_API_KEY="${INPUT_ANTHROPIC_API_KEY}"
REPO_PATH="${GITHUB_WORKSPACE:-/github/workspace}"
OUTPUT_PATH="${INPUT_OUTPUT_PATH:-README.md}"
MODEL="${INPUT_MODEL:-claude-sonnet-5}"
COMMIT_MESSAGE="${INPUT_COMMIT_MESSAGE:-docs: update README via readme-ai-agent}"

echo "Generating README for ${REPO_PATH}..."

uv run --no-dev readme-agent generate \
  --repo-path "${REPO_PATH}" \
  --output "${REPO_PATH}/${OUTPUT_PATH}" \
  --model "${MODEL}" \
  --force

# Commit back via GitHub API
python3 - <<EOF
import os
from pathlib import Path
from readme_agent.github_writer import commit_readme

content = Path("${REPO_PATH}/${OUTPUT_PATH}").read_text()
committed = commit_readme(
    content=content,
    repo=os.environ["GITHUB_REPOSITORY"],
    path="${OUTPUT_PATH}",
    token=os.environ["GITHUB_TOKEN"],
    branch=os.environ.get("GITHUB_REF_NAME", "main"),
    commit_message="${COMMIT_MESSAGE}",
)
if committed:
    print("README committed successfully.")
else:
    print("README unchanged, no commit needed.")
EOF
