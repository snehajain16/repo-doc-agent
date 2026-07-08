import json
from pathlib import Path
from typing import Any

import anthropic

from .models import ReadmeData

SYSTEM_PROMPT = """You are an expert technical writer generating a README for a software project.

You have tools to explore the repository. Use them to understand:
- What the project does
- Primary language and framework
- How to install and run it
- Key dependencies
- Entry points and main files

Be specific and accurate. Do NOT write generic boilerplate. Only include information you found in the repo.

After exploring (use at most 20 tool calls), return a JSON object matching this exact schema:
{
  "project_name": "string",
  "description": "one-line description of what the project does",
  "features": ["list of key features"],
  "prerequisites": ["what needs to be installed"],
  "installation": ["ordered setup steps"],
  "usage_examples": [{"description": "str", "code": "str", "language": "str"}],
  "configuration": [{"name": "str", "description": "str", "default": "str|null", "required": bool}],
  "contributing": "brief contributing note or null",
  "license": "license name or null",
  "badges": []
}

Return ONLY the JSON object as your final message, no markdown fences."""


class ReadmeAgent:
    def __init__(self, model: str = "claude-sonnet-5", verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self.client = anthropic.Anthropic()

    def generate(self, repo_path: Path, tools_schema: list[dict], dispatch_fn: Any) -> ReadmeData:
        messages: list[dict] = []
        tool_calls = 0
        max_tool_calls = 20

        user_message = f"Generate a README for the repository at: {repo_path}\nStart by listing the root files."
        messages.append({"role": "user", "content": user_message})

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=tools_schema,
                messages=messages,
            )

            if self.verbose:
                import sys
                print(f"[agent] stop_reason={response.stop_reason}", file=sys.stderr)

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason == "end_turn":
                # Extract final text response
                for block in assistant_content:
                    if hasattr(block, "text"):
                        return ReadmeData.model_validate_json(block.text)
                raise ValueError("No text block in final response")

            if response.stop_reason != "tool_use" or tool_calls >= max_tool_calls:
                raise ValueError(f"Unexpected stop: {response.stop_reason}, tool_calls={tool_calls}")

            # Process tool calls
            tool_results = []
            for block in assistant_content:
                if block.type != "tool_use":
                    continue
                tool_calls += 1
                if self.verbose:
                    import sys
                    print(f"[tool] {block.name}({block.input})", file=sys.stderr)
                result = dispatch_fn(block.name, block.input, repo_path)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

            messages.append({"role": "user", "content": tool_results})
