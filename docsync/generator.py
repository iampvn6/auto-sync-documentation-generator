from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from docsync.models import ModuleInfo


def generate_module_markdown(module: ModuleInfo) -> str:
    """Generate Markdown API documentation for one Python module."""
    templates_directory = Path(__file__).parent.parent / "templates"

    environment = Environment(
        loader=FileSystemLoader(templates_directory),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = environment.get_template("module_api.md.j2")
    return template.render(module=module)


def save_module_documentation(
    module: ModuleInfo,
    output_directory: str = "docs/api",
) -> Path:
    """Save generated Markdown documentation."""
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    documentation_file = output_path / f"{module.name}.md"
    documentation_file.write_text(
        generate_module_markdown(module),
        encoding="utf-8",
    )

    return documentation_file