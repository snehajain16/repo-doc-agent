from pydantic import BaseModel


class UsageExample(BaseModel):
    description: str
    code: str
    language: str = "bash"


class ConfigItem(BaseModel):
    name: str
    description: str
    default: str | None = None
    required: bool = False


class Badge(BaseModel):
    label: str
    url: str


class ReadmeData(BaseModel):
    project_name: str
    description: str
    features: list[str] = []
    prerequisites: list[str] = []
    installation: list[str] = []
    usage_examples: list[UsageExample] = []
    configuration: list[ConfigItem] = []
    contributing: str | None = None
    license: str | None = None
    badges: list[Badge] = []
