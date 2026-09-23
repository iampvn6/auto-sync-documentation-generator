from pathlib import Path

import yaml
from pydantic import BaseModel

DEFAULT_CONFIG_FILE = ".docsync.yml"


class AiConfig(BaseModel):
    """Optional AI drafting settings (output is always a human-reviewed draft)."""

    enabled: bool = False
    provider: str = "ollama"
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434/v1"
    api_key: str = ""


class DocsyncConfig(BaseModel):
    """Project configuration loaded from .docsync.yml."""

    source_dirs: list[str] = ["examples"]
    docs_dir: str = "docs/api"
    exclude: list[str] = ["tests", ".venv", "__pycache__"]
    fail_on_drift: bool = True
    ai: AiConfig = AiConfig()


def load_config(config_path: str | Path = DEFAULT_CONFIG_FILE) -> DocsyncConfig:
    """Load config from YAML; a missing file or keys falls back to defaults."""
    path = Path(config_path)

    if not path.exists():
        return DocsyncConfig()

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return DocsyncConfig.model_validate(data)


def should_exclude(file_path: Path, config: DocsyncConfig) -> bool:
    """Return True when any path segment matches an excluded directory."""
    return any(excluded in file_path.parts for excluded in config.exclude)
