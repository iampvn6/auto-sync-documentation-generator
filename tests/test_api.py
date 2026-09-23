import pytest
from fastapi.testclient import TestClient

from docsync.api import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    """Use a throwaway SQLite database for every API test."""
    monkeypatch.setattr(
        "docsync.database.DEFAULT_DB_PATH",
        tmp_path / "docsync.db",
    )


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
    assert len(data["functions"]) == 4
    assert data["functions"][0]["name"] == "add"


def test_check_drift_when_documentation_is_current():
    response = client.post(
        "/check-drift",
        json={"file_path": "examples/sample_app/calculator.py"},
    )

    assert response.status_code == 200
    assert response.json()["documentation_current"] is True


def test_check_drift_returns_report_id():
    response = client.post(
        "/check-drift",
        json={"file_path": "examples/sample_app/calculator.py"},
    )

    assert response.status_code == 200
    assert response.json()["report_id"] >= 1


def test_get_report_from_database():
    check_response = client.post(
        "/check-drift",
        json={"file_path": "examples/sample_app/calculator.py"},
    )
    report_id = check_response.json()["report_id"]

    response = client.get(f"/reports/{report_id}")

    assert response.status_code == 200
    assert response.json()["module_name"] == "calculator"
    assert response.json()["status"] == "current"


def test_list_reports():
    client.post(
        "/check-drift",
        json={"file_path": "examples/sample_app/calculator.py"},
    )

    response = client.get("/reports")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["module_name"] == "calculator"
