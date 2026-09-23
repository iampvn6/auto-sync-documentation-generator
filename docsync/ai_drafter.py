"""Optional AI-assisted documentation drafting (always human-reviewed)."""

import httpx

from docsync.config import AiConfig
from docsync.models import ModuleInfo


class LLMUnavailableError(RuntimeError):
    """Raised when the AI provider cannot be reached."""


def build_draft_prompt(
    module: ModuleInfo,
    existing_section: str,
    expected_section: str,
) -> str:
    """Build the prompt asking a model to draft an updated doc section."""
    return (
        f"Module: {module.name}\n"
        f"Source: {module.file_path}\n\n"
        "CURRENT documentation section (what is committed):\n"
        f"{existing_section or '(missing)'}\n\n"
        "EXPECTED documentation section (based on latest source):\n"
        f"{expected_section or '(missing)'}\n\n"
        "Write an updated Markdown section that documents this API. "
        "Use the expected signatures and docstrings. "
        "Output a draft only — a developer must review it before merging."
    )


def draft_documentation(
    module: ModuleInfo,
    existing_section: str,
    expected_section: str,
    ai: AiConfig,
) -> str:
    """Ask an OpenAI-compatible model to draft a doc section (draft only)."""
    url = f"{ai.base_url.rstrip('/')}/chat/completions"

    headers = {"Content-Type": "application/json"}

    if ai.api_key:
        headers["Authorization"] = f"Bearer {ai.api_key}"

    try:
        response = httpx.post(
            url,
            headers=headers,
            json={
                "model": ai.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are DocSync's documentation assistant. You draft "
                            "Markdown API documentation based on Python source "
                            "analysis. Your output is a draft that a developer "
                            "must review before merging."
                        ),
                    },
                    {
                        "role": "user",
                        "content": build_draft_prompt(
                            module,
                            existing_section,
                            expected_section,
                        ),
                    },
                ],
                "temperature": 0.2,
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except Exception as exc:
        raise LLMUnavailableError(
            f"Could not reach LLM at {ai.base_url} ({exc}); "
            "start Ollama or fix the ai section in .docsync.yml."
        ) from exc

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()
