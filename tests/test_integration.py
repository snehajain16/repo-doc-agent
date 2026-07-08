import json
from pathlib import Path
from unittest.mock import MagicMock


from readme_agent.agent import ReadmeAgent
from readme_agent.models import ReadmeData
from readme_agent.tools import TOOLS_SCHEMA, dispatch_tool

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "python-fastapi"

MOCK_README_DATA = {
    "project_name": "Todo API",
    "description": "A REST API for managing todos built with FastAPI.",
    "features": ["CRUD operations for todos", "Auto-generated OpenAPI docs"],
    "prerequisites": ["Python 3.11+", "uvicorn"],
    "installation": ["pip install -r requirements.txt", "uvicorn main:app --reload"],
    "usage_examples": [
        {"description": "List todos", "code": "curl http://localhost:8000/todos", "language": "bash"}
    ],
    "configuration": [],
    "contributing": None,
    "license": None,
    "badges": [],
}


def make_mock_client():
    """Mock Claude: one list_files tool call, then return ReadmeData JSON."""
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

    client.messages.create.side_effect = [tool_response, end_response]
    return client


def test_full_pipeline_with_real_tools():
    """Run the full agent pipeline against the fixture repo with real tools."""
    agent = ReadmeAgent()
    agent.client = make_mock_client()

    result = agent.generate(FIXTURE_PATH, TOOLS_SCHEMA, dispatch_tool)

    assert isinstance(result, ReadmeData)
    assert result.project_name == "Todo API"
    assert len(result.features) > 0


def test_dispatch_tool_list_files_on_fixture():
    """Real list_files call on the fixture repo returns expected files."""
    result = dispatch_tool("list_files", {"path": "."}, FIXTURE_PATH)
    assert isinstance(result, list)
    assert any("main.py" in f for f in result)
    assert any("requirements.txt" in f for f in result)


def test_dispatch_tool_read_file_on_fixture():
    """Real read_file call returns FastAPI content."""
    result = dispatch_tool("read_file", {"path": "main.py"}, FIXTURE_PATH)
    assert "FastAPI" in result
    assert "Todo" in result


def test_dispatch_tool_detect_language_on_fixture():
    """Real detect_language call identifies Python and FastAPI."""
    result = dispatch_tool("detect_language", {}, FIXTURE_PATH)
    assert result["primary"] == "Python"
    assert "FastAPI" in result["frameworks"]


def test_dispatch_tool_read_dependency_file_on_fixture():
    """Real dependency file parsing returns fastapi."""
    result = dispatch_tool("read_dependency_file", {}, FIXTURE_PATH)
    assert "requirements.txt" in result
    assert any("fastapi" in dep.lower() for dep in result["requirements.txt"])


# ── Node/React fixture ────────────────────────────────────────────────────────

NODE_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "node-react"
GO_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "go-cli"


def test_detect_language_node_react():
    result = dispatch_tool("detect_language", {}, NODE_FIXTURE_PATH)
    assert result["primary"] in ("TypeScript", "JavaScript")


def test_read_dependency_file_node_react():
    result = dispatch_tool("read_dependency_file", {}, NODE_FIXTURE_PATH)
    assert "package.json" in result
    assert "react" in result["package.json"]["dependencies"]


def test_list_files_node_react():
    result = dispatch_tool("list_files", {"path": "."}, NODE_FIXTURE_PATH)
    assert any("package.json" in f for f in result)


def test_detect_language_go_cli():
    result = dispatch_tool("detect_language", {}, GO_FIXTURE_PATH)
    assert result["primary"] == "Go"


def test_read_dependency_file_go_cli():
    result = dispatch_tool("read_dependency_file", {}, GO_FIXTURE_PATH)
    assert "go.mod" in result


def test_read_file_go_main():
    result = dispatch_tool("read_file", {"path": "main.go"}, GO_FIXTURE_PATH)
    assert "func main" in result
