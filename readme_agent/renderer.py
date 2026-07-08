from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .models import ReadmeData

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def render(data: ReadmeData) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("readme.md.j2")
    return template.render(data=data)
