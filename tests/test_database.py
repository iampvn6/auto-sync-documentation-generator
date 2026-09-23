from docsync.database import get_scan, list_scans, record_scan


def test_record_and_retrieve_scan(tmp_path):
    db_path = tmp_path / "docsync.db"

    scan_id = record_scan(
        file_path="examples/sample_app/calculator.py",
        module_name="calculator",
        docs_file="docs/api/calculator.md",
        status="current",
        db_path=db_path,
    )

    scan = get_scan(scan_id, db_path=db_path)

    assert scan["module_name"] == "calculator"
    assert scan["status"] == "current"
    assert scan["file_path"] == "examples/sample_app/calculator.py"


def test_get_missing_scan_returns_none(tmp_path):
    assert get_scan(999, db_path=tmp_path / "docsync.db") is None


def test_list_scans_newest_first(tmp_path):
    db_path = tmp_path / "docsync.db"

    record_scan("a.py", "a", "docs/api/a.md", "current", db_path=db_path)
    record_scan("b.py", "b", "docs/api/b.md", "drift_detected", db_path=db_path)

    scans = list_scans(db_path=db_path)
    assert [scan["module_name"] for scan in scans] == ["b", "a"]
