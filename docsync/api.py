from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from docsync.ai_drafter import LLMUnavailableError, draft_documentation
from docsync.analyzer import analyze_python_file
from docsync.config import load_config
from docsync.database import get_scan, list_scans, record_scan
from docsync.drift_checker import check_documentation_drift
from docsync.generator import _generated_section, save_module_documentation

app = FastAPI(
    title="DocSync API",
    description="Generate Python API documentation automatically.",
    version="0.1.0",
)


class ScanRequest(BaseModel):
    file_path: str


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}


def _validate_python_file(file_path: str) -> Path:
    path = Path(file_path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Python file not found.")

    if path.suffix != ".py":
        raise HTTPException(status_code=400, detail="Only Python files are supported.")

    return path


@app.post("/scan")
def scan_python_file(request: ScanRequest) -> dict:
    path = _validate_python_file(request.file_path)
    module = analyze_python_file(path)
    return module.model_dump()


@app.post("/generate-docs")
def generate_documentation(request: ScanRequest) -> dict:
    path = _validate_python_file(request.file_path)
    module = analyze_python_file(path)
    documentation_file = save_module_documentation(module)

    return {
        "status": "generated",
        "module": module.name,
        "documentation_file": str(documentation_file),
    }


@app.post("/check-drift")
def check_drift(request: ScanRequest) -> dict:
    path = _validate_python_file(request.file_path)
    module = analyze_python_file(path)

    is_current = check_documentation_drift(path)
    report_id = record_scan(
        file_path=str(path),
        module_name=module.name,
        docs_file=str(Path("docs/api") / f"{module.name}.md"),
        status="current" if is_current else "drift_detected",
    )

    return {
        "report_id": report_id,
        "file_path": str(path),
        "status": "current" if is_current else "drift_detected",
        "documentation_current": is_current,
    }


@app.get("/reports/{report_id}")
def get_report(report_id: int) -> dict:
    report = get_scan(report_id)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    return report


@app.get("/reports")
def list_reports(limit: int = 20) -> list[dict]:
    return list_scans(limit=limit)


@app.post("/ai-draft")
def ai_draft(request: ScanRequest) -> dict:
    """Draft an updated doc section with an LLM (human review required)."""
    path = _validate_python_file(request.file_path)
    config = load_config()

    if not config.ai.enabled:
        raise HTTPException(status_code=400, detail="AI drafting is disabled.")

    module = analyze_python_file(path)
    expected_section = _generated_section(module)

    documentation_file = Path("docs/api") / f"{module.name}.md"
    existing_section = (
        documentation_file.read_text(encoding="utf-8")
        if documentation_file.exists()
        else ""
    )

    try:
        draft = draft_documentation(
            module,
            existing_section,
            expected_section,
            config.ai,
        )
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "module": module.name,
        "status": "draft",
        "draft": draft,
        "review_required": True,
    }
