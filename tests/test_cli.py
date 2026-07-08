from unittest.mock import MagicMock, patch
import json

from click.testing import CliRunner

from readme_agent.cli import cli
from readme_agent.models import ReadmeData

SAMPLE_DATA = ReadmeData(
    project_name="MyApp",
    description="A sample application.",
    features=["Fast", "Reliable"],
    prerequisites=["Python 3.11+"],
    installation=["pip install myapp"],
    usage_examples=[],
    configuration=[],
    contributing=None,
    license="MIT",
    badges=[],
)


def make_mock_agent(data: ReadmeData = SAMPLE_DATA):
    mock = MagicMock()
    mock.generate.return_value = data
    return mock


def test_generate_writes_readme(tmp_path):
    runner = CliRunner()
    with patch("readme_agent.cli.ReadmeAgent") as MockAgent:
        MockAgent.return_value = make_mock_agent()
        result = runner.invoke(cli, ["generate", "--repo-path", str(tmp_path), "--output", str(tmp_path / "README.md"), "--force"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "README.md").exists()
    assert "MyApp" in (tmp_path / "README.md").read_text()


def test_generate_json_flag(tmp_path):
    runner = CliRunner()
    with patch("readme_agent.cli.ReadmeAgent") as MockAgent:
        MockAgent.return_value = make_mock_agent()
        result = runner.invoke(cli, ["generate", "--repo-path", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.output
    parsed = json.loads(result.output)
    assert parsed["project_name"] == "MyApp"


def test_generate_invalid_repo_path():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "--repo-path", "/nonexistent/path/xyz"])
    assert result.exit_code != 0


def test_generate_prompts_before_overwrite(tmp_path):
    existing = tmp_path / "README.md"
    existing.write_text("existing content")
    runner = CliRunner()
    with patch("readme_agent.cli.ReadmeAgent") as MockAgent:
        MockAgent.return_value = make_mock_agent()
        # Simulate user saying "n" to overwrite prompt
        result = runner.invoke(cli, ["generate", "--repo-path", str(tmp_path), "--output", str(existing)], input="n\n")
    assert result.exit_code != 0  # aborted


def test_generate_force_skips_prompt(tmp_path):
    existing = tmp_path / "README.md"
    existing.write_text("old content")
    runner = CliRunner()
    with patch("readme_agent.cli.ReadmeAgent") as MockAgent:
        MockAgent.return_value = make_mock_agent()
        result = runner.invoke(cli, ["generate", "--repo-path", str(tmp_path), "--output", str(existing), "--force"])
    assert result.exit_code == 0, result.output
    assert "MyApp" in existing.read_text()
