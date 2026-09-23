from docsync.analyzer import analyze_python_file
from docsync.drift_checker import check_documentation_drift
from docsync.generator import generate_module_markdown, save_module_documentation

SAMPLE = "examples/sample_app/calculator.py"


def test_save_creates_new_file(tmp_path):
    module = analyze_python_file(SAMPLE)
    output_file = save_module_documentation(module, output_directory=tmp_path)

    content = output_file.read_text(encoding="utf-8")
    assert "# API Reference: `calculator`" in content
    assert "add(first_number: int, second_number: int, tax: int = 0) -> int" in content


def test_save_preserves_manual_notes(tmp_path):
    module = analyze_python_file(SAMPLE)

    (tmp_path / "calculator.md").write_text(
        "# Team title\n\n"
        "<!-- DOCSYNC:START -->\nOLD CONTENT\n<!-- DOCSYNC:END -->\n\n"
        "> Manual notes — do not delete.\n",
        encoding="utf-8",
    )

    save_module_documentation(module, output_directory=tmp_path)

    content = (tmp_path / "calculator.md").read_text(encoding="utf-8")
    assert "Team title" in content  # manual header kept
    assert "Manual notes — do not delete." in content  # manual footer kept
    assert "OLD CONTENT" not in content  # stale block replaced
    assert "tax: int = 0" in content  # fresh content written


def test_drift_ignores_manual_notes(tmp_path):
    module = analyze_python_file(SAMPLE)
    markdown = generate_module_markdown(module)

    (tmp_path / "calculator.md").write_text(
        "# Custom title\n\n" + markdown + "\n\nCustom footer notes.\n",
        encoding="utf-8",
    )

    assert check_documentation_drift(SAMPLE, docs_directory=tmp_path) is True
