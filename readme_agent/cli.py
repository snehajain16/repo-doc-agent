import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .agent import ReadmeAgent
from .models import ReadmeData
from .renderer import render
from .tools import TOOLS_SCHEMA, dispatch_tool

console = Console(stderr=True)
out_console = Console()


@click.group()
def cli() -> None:
    """README AI Agent — generate accurate READMEs using Claude."""


@cli.command()
@click.option("--repo-path", default=".", show_default=True, help="Path to the repository.")
@click.option("--output", default="README.md", show_default=True, help="Output file path.")
@click.option("--model", default="claude-sonnet-5", show_default=True, help="Claude model to use.")
@click.option("--verbose", is_flag=True, help="Print agent tool calls to stderr.")
@click.option("--force", is_flag=True, help="Overwrite existing output file without prompting.")
@click.option("--json", "as_json", is_flag=True, help="Print ReadmeData as JSON to stdout instead of writing file.")
def generate(
    repo_path: str,
    output: str,
    model: str,
    verbose: bool,
    force: bool,
    as_json: bool,
) -> None:
    """Generate a README for a repository using Claude."""
    repo = Path(repo_path).resolve()
    if not repo.exists():
        console.print(f"[red]Error:[/red] Repository path does not exist: {repo}")
        sys.exit(1)

    out_path = Path(output)
    if not as_json and out_path.exists() and not force:
        click.confirm(f"{output} already exists. Overwrite?", abort=True)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, transient=True) as progress:
        progress.add_task("Exploring repository and generating README...", total=None)
        agent = ReadmeAgent(model=model, verbose=verbose)
        data: ReadmeData = agent.generate(repo, TOOLS_SCHEMA, dispatch_tool)

    if as_json:
        out_console.print(data.model_dump_json(indent=2))
        return

    readme_content = render(data)
    out_path.write_text(readme_content, encoding="utf-8")
    console.print(f"[green]✓[/green] README written to [bold]{out_path}[/bold]")
