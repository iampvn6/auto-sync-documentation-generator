from pathlib import Path

from docsync.analyzer import analyze_python_file
from docsync.generator import generate_module_markdown


def check_documentation_drift(
    python_file: str | Path,
    docs_directory: str | Path = "docs/api",
) -> bool:
    """
    Return True when documentation is current.
    Return False when documentation is missing or outdated.
    """
    module = analyze_python_file(python_file)

    documentation_file = Path(docs_directory) / f"{module.name}.md"

    if not documentation_file.exists():
        return False

    expected_documentation = generate_module_markdown(module)
    existing_documentation = documentation_file.read_text(encoding="utf-8")

    return existing_documentation == expected_documentation
