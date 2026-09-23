from unittest.mock import Mock

import pytest

from docsync.ai_drafter import (
    LLMUnavailableError,
    build_draft_prompt,
    draft_documentation,
)
from docsync.analyzer import analyze_python_file
from docsync.config import AiConfig
from docsync.generator import _generated_section

SAMPLE = "examples/sample_app/calculator.py"


def test_build_draft_prompt_contains_expected_signature():
    module = analyze_python_file(SAMPLE)

    prompt = build_draft_prompt(module, "(missing)", _generated_section(module))

    assert "calculator" in prompt
    assert "add(first_number: int, second_number: int, tax: int = 0) -> int" in prompt
    assert "expected" in prompt.lower()


def test_draft_documentation_returns_model_content(monkeypatch):
    fake_response = Mock()
    fake_response.raise_for_status = Mock()
    fake_response.json.return_value = {
        "choices": [{"message": {"content": "# Draft docs\n\nUpdated."}}]
    }
    monkeypatch.setattr(
        "docsync.ai_drafter.httpx.post",
        Mock(return_value=fake_response),
    )

    module = analyze_python_file(SAMPLE)
    draft = draft_documentation(
        module,
        "(missing)",
        _generated_section(module),
        AiConfig(),
    )

    assert draft == "# Draft docs\n\nUpdated."


def test_draft_documentation_raises_when_llm_unreachable(monkeypatch):
    def failing_post(*args, **kwargs):
        raise ConnectionError("connection refused")

    monkeypatch.setattr("docsync.ai_drafter.httpx.post", failing_post)

    module = analyze_python_file(SAMPLE)

    with pytest.raises(LLMUnavailableError):
        draft_documentation(module, "", "", AiConfig())
