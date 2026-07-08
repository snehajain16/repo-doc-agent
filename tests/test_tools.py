import json
from pathlib import Path

import pytest

from readme_agent.tools import (
    _safe_path,
    list_files,
    read_file,
    search_code,
    detect_language,
    read_dependency_file,
    dispatch_tool,
    TOOLS_SCHEMA,
)


@pytest.fixture
def repo(tmp_path):
    """Create a minimal fake repo for testing."""
    (tmp_path / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
    (tmp_path / "requirements.txt").write_text("fastapi==0.110.0\nuvicorn>=0.29.0\n")
    (tmp_path / "README.md").write_text("# My Project\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "utils.py").write_text("def helper(): pass\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("[core]\n")
    pkg = {"name": "my-app", "version": "1.0.0", "dependencies": {"react": "^18.0.0"}, "devDependencies": {"typescript": "^5.0.0"}, "scripts": {"start": "node index.js"}}
    (tmp_path / "package.json").write_text(json.dumps(pkg))
    return tmp_path


def test_safe_path_valid(repo):
    p = _safe_path("main.py", repo)
    assert p == (repo / "main.py").resolve()


def test_safe_path_traversal_rejected(repo):
    with pytest.raises(ValueError, match="traversal"):
        _safe_path("../../etc/passwd", repo)


def test_list_files_root(repo):
    files = list_files(".", repo)
    assert any("main.py" in f for f in files)
    assert not any(".git" in f for f in files)


def test_list_files_subdir(repo):
    files = list_files("src", repo)
    assert any("utils.py" in f for f in files)


def test_list_files_nonexistent(repo):
    assert list_files("nonexistent", repo) == []


def test_read_file_content(repo):
    content = read_file("main.py", repo)
    assert "FastAPI" in content


def test_read_file_truncation(repo):
    big_file = repo / "big.txt"
    big_file.write_text("x" * 10000)
    content = read_file("big.txt", repo)
    assert len(content) < 10000
    assert "truncated" in content


def test_read_file_not_found(repo):
    result = read_file("missing.py", repo)
    assert "not found" in result.lower()


def test_read_file_traversal_rejected(repo):
    with pytest.raises(ValueError, match="traversal"):
        read_file("../../etc/passwd", repo)


def test_search_code_finds_match(repo):
    results = search_code("FastAPI", repo)
    assert len(results) > 0
    assert results[0]["file"] == "main.py"


def test_search_code_no_match(repo):
    results = search_code("xyzzy_not_found_123", repo)
    assert results == []


def test_search_code_invalid_regex(repo):
    results = search_code("[invalid", repo)
    assert results[0].get("error")


def test_detect_language_python(repo):
    result = detect_language(repo)
    assert result["primary"] == "Python"
    assert "FastAPI" in result["frameworks"]


def test_read_dependency_file_requirements(repo):
    result = read_dependency_file(repo)
    assert "requirements.txt" in result
    assert any("fastapi" in dep.lower() for dep in result["requirements.txt"])


def test_read_dependency_file_package_json(repo):
    result = read_dependency_file(repo)
    assert "package.json" in result
    assert "react" in result["package.json"]["dependencies"]


def test_tools_schema_has_all_tools(repo):
    names = {t["name"] for t in TOOLS_SCHEMA}
    assert names == {"list_files", "read_file", "search_code", "detect_language", "read_dependency_file"}


def test_dispatch_tool_list_files(repo):
    result = dispatch_tool("list_files", {"path": "."}, repo)
    assert isinstance(result, list)


def test_dispatch_tool_unknown(repo):
    result = dispatch_tool("unknown_tool", {}, repo)
    assert "Unknown" in str(result)
