from pathlib import Path

from docsync.analyzer import analyze_python_file
from docsync.generator import END_MARKER, START_MARKER, _generated_section


def check_documentation_drift(
    python_file: str | Path,
    docs_directory: str | Path = "docs/api",
) -> bool:
    """Return True when the generated section matches the current code."""
    module = analyze_python_file(python_file)

    documentation_file = Path(docs_directory) / f"{module.name}.md"

    if not documentation_file.exists():
        return False

    expected = _generated_section(module)
    existing = documentation_file.read_text(encoding="utf-8")

    if START_MARKER in existing and END_MARKER in existing:
        start = existing.index(START_MARKER)
        end = existing.index(END_MARKER) + len(END_MARKER)
        existing = existing[start:end]

    return existing == expected
