import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from readme_agent.agent import ReadmeAgent
from readme_agent.models import ReadmeData


MOCK_README_DATA = {
    "project_name": "test-project",
    "description": "A test project",
    "features": ["Feature A"],
    "prerequisites": ["Python 3.11+"],
    "installation": ["pip install test-project"],
    "usage_examples": [],
    "configuration": [],
    "contributing": None,
    "license": "MIT",
    "badges": [],
}


def make_mock_client(tool_calls_before_end: int = 1):
    client = MagicMock()

    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "list_files"
    tool_block.input = {"path": "."}
    tool_block.id = "call_1"
    tool_response.content = [tool_block]

    end_response = MagicMock()
    end_response.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.text = json.dumps(MOCK_README_DATA)
    end_response.content = [text_block]

    responses = [tool_response] * tool_calls_before_end + [end_response]
    client.messages.create.side_effect = responses
    return client


def test_agent_returns_readme_data(tmp_path):
    agent = ReadmeAgent()
    mock_client = make_mock_client(tool_calls_before_end=1)
    agent.client = mock_client

    tools_schema = [{"name": "list_files", "description": "list files", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}]
    dispatch_fn = MagicMock(return_value=["README.md", "main.py"])

    result = agent.generate(tmp_path, tools_schema, dispatch_fn)

    assert isinstance(result, ReadmeData)
    assert result.project_name == "test-project"
    assert result.license == "MIT"


def test_agent_respects_max_tool_calls(tmp_path):
    agent = ReadmeAgent()
    # After 20 tool calls, should raise
    mock_client = make_mock_client(tool_calls_before_end=21)
    agent.client = mock_client

    tools_schema = [{"name": "list_files", "description": "list files", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}]
    dispatch_fn = MagicMock(return_value=[])

    with pytest.raises(ValueError, match="Unexpected stop"):
        agent.generate(tmp_path, tools_schema, dispatch_fn)
