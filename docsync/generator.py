from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from docsync.models import ModuleInfo

TEMPLATES_DIRECTORY = Path(__file__).parent.parent / "templates"
START_MARKER = "<!-- DOCSYNC:START -->"
END_MARKER = "<!-- DOCSYNC:END -->"


def generate_module_markdown(module: ModuleInfo) -> str:
    """Generate the full Markdown API reference for one Python module."""
    environment = Environment(
        loader=FileSystemLoader(TEMPLATES_DIRECTORY),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = environment.get_template("module_api.md.j2")
    return template.render(module=module)


def _generated_section(module: ModuleInfo) -> str:
    """The regenerable block between (and including) the DOCSYNC markers."""
    markdown = generate_module_markdown(module)
    start = markdown.index(START_MARKER)
    end = markdown.index(END_MARKER) + len(END_MARKER)
    return markdown[start:end]


def save_module_documentation(
    module: ModuleInfo,
    output_directory: str | Path = "docs/api",
) -> Path:
    """Write docs, preserving any manual content outside the markers."""
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    documentation_file = output_path / f"{module.name}.md"
    generated_section = _generated_section(module)

    if documentation_file.exists():
        existing = documentation_file.read_text(encoding="utf-8")

        if START_MARKER in existing and END_MARKER in existing:
            before = existing[: existing.index(START_MARKER)]
            after = existing[existing.index(END_MARKER) + len(END_MARKER) :]
            documentation_file.write_text(
                before + generated_section + after,
                encoding="utf-8",
            )
            return documentation_file

    # New file, or existing file without markers: write the full document.
    documentation_file.write_text(
        generate_module_markdown(module),
        encoding="utf-8",
    )
    return documentation_file
