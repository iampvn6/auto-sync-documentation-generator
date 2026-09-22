from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from docsync.git_diff import get_changed_python_files


@patch("docsync.git_diff.subprocess.run")
def test_get_changed_python_files(mock_run):
    mock_run.return_value = CompletedProcess(
        args=[],
        returncode=0,
        stdout=(
            "docs/api/calculator.md\n"
            "docsync/analyzer.py\n"
            "examples/sample_app/calculator.py\n"
            "README.md\n"
        ),
    )

    changed_files = get_changed_python_files()

    assert changed_files == [
        Path("docsync/analyzer.py"),
        Path("examples/sample_app/calculator.py"),
    ]

    mock_run.assert_called_once_with(
        ["git", "diff", "--name-only", "main...HEAD"],
        capture_output=True,
        check=True,
        text=True,
    )
