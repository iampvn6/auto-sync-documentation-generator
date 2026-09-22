from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from docsync.analyzer import analyze_python_file
from docsync.generator import save_module_documentation
from docsync.drift_checker import check_documentation_drift

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


@app.post("/scan")
def scan_python_file(request: ScanRequest) -> dict:
    path = Path(request.file_path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Python file not found.")

    if path.suffix != ".py":
        raise HTTPException(status_code=400, detail="Only Python files are supported.")

    module = analyze_python_file(path)
    return module.model_dump()


@app.post("/generate-docs")
def generate_documentation(request: ScanRequest) -> dict:
    path = Path(request.file_path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Python file not found.")

    if path.suffix != ".py":
        raise HTTPException(status_code=400, detail="Only Python files are supported.")

    module = analyze_python_file(path)
    documentation_file = save_module_documentation(module)

    return {
        "status": "generated",
        "module": module.name,
        "documentation_file": str(documentation_file),
    }
    
@app.post("/check-drift")
def check_drift(request: ScanRequest) -> dict:
    path = Path(request.file_path)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Python file not found.")

    if path.suffix != ".py":
        raise HTTPException(status_code=400, detail="Only Python files are supported.")

    is_current = check_documentation_drift(path)

    return {
        "file_path": str(path),
        "status": "current" if is_current else "drift_detected",
        "documentation_current": is_current,
    }