from pathlib import Path

import typer

from docsync.ai_drafter import LLMUnavailableError, draft_documentation
from docsync.analyzer import analyze_python_file
from docsync.config import load_config, should_exclude
from docsync.drift_checker import check_documentation_drift
from docsync.generator import _generated_section, save_module_documentation
from docsync.git_diff import get_changed_python_files

app = typer.Typer(help="Generate and check Python API documentation.")


def _python_files(directory: str | None, config) -> list[Path]:
    directories = [directory] if directory else config.source_dirs

    return [
        file_path
        for source_directory in directories
        for file_path in Path(source_directory).rglob("*.py")
        if not should_exclude(file_path, config)
    ]


@app.command()
def generate(
    source_directory: str | None = typer.Argument(
        None,
        help="Directory to scan (overrides config).",
    ),
) -> None:
    """Generate Markdown documentation for Python files."""
    config = load_config()

    for file_path in _python_files(source_directory, config):
        module = analyze_python_file(file_path)
        output_file = save_module_documentation(module, config.docs_dir)
        typer.echo(f"Generated: {output_file}")


@app.command()
def check(
    source_directory: str | None = typer.Argument(
        None,
        help="Directory to scan (overrides config).",
    ),
    base: str | None = typer.Option(
        None,
        "--base",
        help="Check only Python files changed since this Git branch.",
    ),
) -> None:
    """Check whether Markdown documentation matches Python code."""
    config = load_config()

    if base:
        python_files = [
            file_path
            for file_path in get_changed_python_files(base)
            if file_path.exists() and not should_exclude(file_path, config)
        ]
    else:
        python_files = _python_files(source_directory, config)

    if not python_files:
        typer.echo("No Python files to check.")
        return

    outdated_files = []

    for file_path in python_files:
        is_current = check_documentation_drift(
            file_path,
            docs_directory=config.docs_dir,
        )

        if is_current:
            typer.echo(f"Current: {file_path}")
        else:
            typer.echo(f"Outdated or missing documentation: {file_path}")
            outdated_files.append(file_path)

    if outdated_files and config.fail_on_drift:
        raise typer.Exit(code=1)


@app.command()
def draft(
    source_directory: str | None = typer.Argument(
        None,
        help="Directory to scan (overrides config).",
    ),
) -> None:
    """Draft doc updates with an LLM for modules with drift (human review required)."""
    config = load_config()

    if not config.ai.enabled:
        typer.echo("AI drafting is disabled (set ai.enabled: true in .docsync.yml).")
        raise typer.Exit(code=0)

    for file_path in _python_files(source_directory, config):
        module = analyze_python_file(file_path)
        documentation_file = Path(config.docs_dir) / f"{module.name}.md"

        if not documentation_file.exists():
            continue

        existing = documentation_file.read_text(encoding="utf-8")
        start = existing.index("<!-- DOCSYNC:START -->")
        stop = existing.index("<!-- DOCSYNC:END -->") + len("<!-- DOCSYNC:END -->")
        existing_section = existing[start:stop]
        expected_section = _generated_section(module)

        if existing_section == expected_section:
            typer.echo(f"Current: {file_path}")
            continue

        try:
            draft_markdown = draft_documentation(
                module,
                existing_section,
                expected_section,
                config.ai,
            )
        except LLMUnavailableError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc

        typer.echo(f"\nDraft for {file_path} (review before merging):\n")
        typer.echo(draft_markdown)


if __name__ == "__main__":
    app()
