# Auto-Sync Documentation Generator (DocSync)

DocSync is a Python developer tool that detects documentation drift when Python code changes and generates updated Markdown API references.

It uses Python's Abstract Syntax Tree (AST) to inspect function signatures, type annotations, default values, and docstrings without executing application code. A FastAPI backend and command-line interface expose the same functionality for local development and automation.

## Features

- Analyzes Python functions using the built-in `ast` module
- Extracts function signatures, type annotations, default values, and docstrings
- Generates Markdown API documentation with Jinja2 templates
- Detects when committed documentation no longer matches source code
- Provides CLI commands to generate and check documentation
- Provides FastAPI endpoints for scanning, generation, and drift checking
- Includes automated tests with Pytest

## Tech Stack

- Python 3.12
- FastAPI and Uvicorn
- Pydantic
- Jinja2
- Python AST
- Typer
- Pytest
- Ruff and Black

## Project Structure

```text
docsync/
├── docsync/                 # Application source code
├── docs/api/                # Generated Markdown API references
├── examples/sample_app/     # Example Python module
├── templates/               # Jinja2 documentation templates
├── tests/                   # Automated tests
└── pyproject.toml           # Tool configuration
```

## Setup

```bash
git clone git@github.com:iampvn6/auto-sync-documentation-generator.git
cd auto-sync-documentation-generator

python3 -m venv .venv
source .venv/bin/activate

pip install fastapi "uvicorn[standard]" typer jinja2 pydantic pytest ruff black pyyaml httpx
```

## Generate Documentation

Generate API documentation for Python modules:

```bash
python -m docsync.cli generate examples/sample_app
```

Generated documentation is saved in `docs/api/`.

## Check for Documentation Drift

Check whether generated documentation matches the current Python source:

```bash
python -m docsync.cli check examples/sample_app
```

When documentation is current:

```text
Current: examples/sample_app/calculator.py
```

When a function signature or docstring changes without regenerating documentation:

```text
Outdated or missing documentation: examples/sample_app/calculator.py
```

## Run the API

```bash
uvicorn docsync.api:app --reload
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

- `GET /health` — service health check
- `POST /scan` — analyze one Python file
- `POST /generate-docs` — generate Markdown documentation
- `POST /check-drift` — check whether documentation is current

Example request body:

```json
{
  "file_path": "examples/sample_app/calculator.py"
}
```

## Run Tests

```bash
pytest
ruff check .
black --check .
```

## Workflow

```text
Python code change
        ↓
AST analyzer extracts the current API
        ↓
DocSync generates expected Markdown documentation
        ↓
Drift checker compares it with existing documentation
        ↓
CLI or FastAPI reports whether docs are current
```

## Future Enhancements

- Detect changed files from Git pull-request diffs
- Run documentation checks in GitHub Actions
- Support classes and class methods
- Preserve manual content outside generated documentation markers
- Store scan history in SQLite
- Use an optional LLM to draft documentation updates for developer review

## Author

Pavan Kumar V N — [GitHub](https://github.com/iampvn6)
