import pytest
from pydantic import ValidationError

from readme_agent.models import ReadmeData, UsageExample, ConfigItem


def test_readme_data_minimal():
    data = ReadmeData(project_name="MyApp", description="A cool app")
    assert data.project_name == "MyApp"
    assert data.features == []
    assert data.license is None


def test_readme_data_full():
    data = ReadmeData(
        project_name="MyApp",
        description="A cool app",
        features=["Fast", "Reliable"],
        prerequisites=["Python 3.11+"],
        installation=["git clone ...", "pip install ."],
        usage_examples=[{"description": "Run it", "code": "python main.py", "language": "bash"}],
        configuration=[{"name": "API_KEY", "description": "Your API key", "required": True}],
        contributing="Open a PR",
        license="MIT",
        badges=[{"label": "CI", "url": "https://example.com/badge"}],
    )
    assert len(data.features) == 2
    assert data.usage_examples[0].language == "bash"
    assert data.configuration[0].required is True
    assert data.badges[0].label == "CI"


def test_readme_data_missing_required_fields():
    with pytest.raises(ValidationError):
        ReadmeData(description="Missing project_name")


def test_usage_example_default_language():
    ex = UsageExample(description="test", code="echo hi")
    assert ex.language == "bash"


def test_config_item_defaults():
    item = ConfigItem(name="FOO", description="bar")
    assert item.default is None
    assert item.required is False
