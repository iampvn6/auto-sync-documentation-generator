from pathlib import Path

import typer

from docsync.analyzer import analyze_python_file
from docsync.drift_checker import check_documentation_drift
from docsync.generator import save_module_documentation
from docsync.git_diff import get_changed_python_files

app = typer.Typer(help="Generate and check Python API documentation.")


@app.command()
def generate(source_directory: str) -> None:
    """Generate Markdown documentation for Python files."""
    for file_path in Path(source_directory).rglob("*.py"):
        if "__pycache__" in file_path.parts:
            continue

        module = analyze_python_file(file_path)
        output_file = save_module_documentation(module)

        typer.echo(f"Generated: {output_file}")


@app.command()
def check(
    source_directory: str,
    base: str | None = typer.Option(
        None,
        "--base",
        help="Check only Python files changed since this Git branch.",
    ),
) -> None:
    """Check whether Markdown documentation matches Python code."""
    if base:
        python_files = [
            file_path
            for file_path in get_changed_python_files(base)
            if file_path.exists()
        ]
    else:
        python_files = [
            file_path
            for file_path in Path(source_directory).rglob("*.py")
            if "__pycache__" not in file_path.parts
        ]

    if not python_files:
        typer.echo("No Python files to check.")
        return

    outdated_files = []

    for file_path in python_files:
        is_current = check_documentation_drift(file_path)

        if is_current:
            typer.echo(f"Current: {file_path}")
        else:
            typer.echo(f"Outdated or missing documentation: {file_path}")
            outdated_files.append(file_path)

    if outdated_files:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
