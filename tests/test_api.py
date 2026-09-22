from fastapi.testclient import TestClient

from docsync.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_scan_python_file():
    response = client.post(
        "/scan",
        json={"file_path": "examples/sample_app/calculator.py"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "calculator"
    assert len(data["functions"]) == 2
    assert data["functions"][0]["name"] == "add"


def test_check_drift_when_documentation_is_current():
    response = client.post(
        "/check-drift",
        json={"file_path": "examples/sample_app/calculator.py"},
    )

    assert response.status_code == 200
    assert response.json()["documentation_current"] is True
