import subprocess
from pathlib import Path


def get_changed_python_files(base_branch: str = "main") -> list[Path]:
    """Return Python files changed compared with a Git base branch."""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_branch}...HEAD"],
        capture_output=True,
        check=True,
        text=True,
    )

    changed_files = []

    for file_name in result.stdout.splitlines():
        file_path = Path(file_name)

        if file_path.suffix == ".py":
            changed_files.append(file_path)

    return changed_files
