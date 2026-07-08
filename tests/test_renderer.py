from readme_agent.models import ReadmeData, UsageExample, ConfigItem
from readme_agent.renderer import render


SAMPLE_DATA = ReadmeData(
    project_name="FastAPI App",
    description="A high-performance REST API built with FastAPI.",
    features=["Async request handling", "Auto-generated OpenAPI docs"],
    prerequisites=["Python 3.11+", "uv package manager"],
    installation=["git clone https://github.com/example/app", "uv sync", "uv run uvicorn main:app"],
    usage_examples=[
        UsageExample(
            description="Start the development server:",
            code="uv run uvicorn main:app --reload",
            language="bash",
        )
    ],
    configuration=[
        ConfigItem(name="DATABASE_URL", description="PostgreSQL connection string", required=True),
        ConfigItem(name="DEBUG", description="Enable debug mode", default="false", required=False),
    ],
    contributing="Fork the repo and open a pull request.",
    license="MIT",
)


def test_render_contains_project_name():
    output = render(SAMPLE_DATA)
    assert "# FastAPI App" in output


def test_render_contains_description():
    output = render(SAMPLE_DATA)
    assert "high-performance REST API" in output


def test_render_contains_features():
    output = render(SAMPLE_DATA)
    assert "## Features" in output
    assert "Async request handling" in output


def test_render_contains_installation():
    output = render(SAMPLE_DATA)
    assert "## Installation" in output
    assert "uv sync" in output


def test_render_contains_usage():
    output = render(SAMPLE_DATA)
    assert "## Usage" in output
    assert "uvicorn main:app --reload" in output


def test_render_contains_config_table():
    output = render(SAMPLE_DATA)
    assert "## Configuration" in output
    assert "DATABASE_URL" in output
    assert "Yes" in output


def test_render_contains_license():
    output = render(SAMPLE_DATA)
    assert "## License" in output
    assert "MIT" in output


def test_render_omits_empty_sections():
    minimal = ReadmeData(project_name="Minimal", description="Just a description")
    output = render(minimal)
    assert "## Features" not in output
    assert "## Installation" not in output
    assert "## Configuration" not in output
