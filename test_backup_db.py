import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

import backup_db


def make_db(path: Path, value: str) -> None:
    with closing(sqlite3.connect(path)) as conn:
        with conn:
            conn.execute("CREATE TABLE notes (value TEXT NOT NULL)")
            conn.execute("INSERT INTO notes(value) VALUES (?)", (value,))


def read_value(path: Path) -> str:
    with closing(sqlite3.connect(path)) as conn:
        return conn.execute("SELECT value FROM notes").fetchone()[0]


def test_backup_creates_integrity_checked_independent_copy(tmp_path):
    source = tmp_path / "source.sqlite3"
    make_db(source, "original")
    backup = backup_db.backup_database(source, tmp_path / "backups")
    assert backup.exists()
    assert backup != source
    assert read_value(backup) == "original"
    backup_db.integrity_check(backup)


def test_integrity_check_closes_sqlite_connection(tmp_path, monkeypatch):
    database = tmp_path / "connection-lifecycle.sqlite3"
    make_db(database, "test")
    original_connect = sqlite3.connect
    connection = original_connect(database)
    monkeypatch.setattr(backup_db.sqlite3, "connect", lambda *args, **kwargs: connection)

    backup_db.integrity_check(database)

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_restore_preserves_safety_copy_and_restores_data(tmp_path):
    source = tmp_path / "backup.sqlite3"
    destination = tmp_path / "live.sqlite3"
    make_db(source, "from-backup")
    make_db(destination, "current-data")
    safety_copy = backup_db.restore_database(source, destination)
    assert safety_copy is not None and safety_copy.exists()
    assert read_value(safety_copy) == "current-data"
    assert read_value(destination) == "from-backup"


def test_restore_invalid_source_does_not_change_destination(tmp_path):
    source = tmp_path / "corrupt.sqlite3"
    destination = tmp_path / "live.sqlite3"
    source.write_bytes(b"not a sqlite database")
    make_db(destination, "must-survive")
    with pytest.raises(sqlite3.DatabaseError):
        backup_db.restore_database(source, destination)
    assert read_value(destination) == "must-survive"


def test_restore_rejects_same_source_and_destination(tmp_path):
    database = tmp_path / "same.sqlite3"
    make_db(database, "safe")
    with pytest.raises(ValueError, match="origen"):
        backup_db.restore_database(database, database)
    assert read_value(database) == "safe"


def test_backup_rejects_missing_database(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup_db.backup_database(tmp_path / "missing.sqlite3", tmp_path / "backups")


def test_restore_cleans_temporary_file_after_invalid_source(tmp_path):
    source = tmp_path / "corrupt.sqlite3"
    destination = tmp_path / "live.sqlite3"
    source.write_bytes(b"invalid")
    make_db(destination, "keep")
    with pytest.raises(sqlite3.DatabaseError):
        backup_db.restore_database(source, destination)
    assert not list(tmp_path.glob(".*.restore.tmp"))
    assert read_value(destination) == "keep"


def test_inspect_reports_integrity_without_modifying_database(tmp_path):
    database = tmp_path / "inspect.sqlite3"
    make_db(database, "inspect-me")
    before = database.read_bytes()
    report = backup_db.inspect_database(database)
    assert report["integrity"] == "ok"
    assert report["table_count"] == 1
    assert report["size_bytes"] > 0
    assert database.read_bytes() == before


def test_inspect_rejects_corrupt_database(tmp_path):
    database = tmp_path / "corrupt.sqlite3"
    database.write_bytes(b"not sqlite")
    with pytest.raises(sqlite3.DatabaseError):
        backup_db.inspect_database(database)


def test_backup_includes_committed_wal_data(tmp_path):
    source = tmp_path / "wal-source.sqlite3"
    with sqlite3.connect(source) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE notes (value TEXT NOT NULL)")
        conn.execute("INSERT INTO notes(value) VALUES ('before-checkpoint')")
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("INSERT INTO notes(value) VALUES ('after-checkpoint')")
        conn.commit()
        # Keep the connection open so the WAL remains active during backup.
        backup = backup_db.backup_database(source, tmp_path / "backups")
        values = [row[0] for row in sqlite3.connect(backup).execute("SELECT value FROM notes ORDER BY rowid")]
        assert values == ["before-checkpoint", "after-checkpoint"]


def test_inspect_reports_wal_mode_for_persistent_database(tmp_path):
    database = tmp_path / "persistent.sqlite3"
    with sqlite3.connect(database) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE notes (value TEXT NOT NULL)")
        conn.execute("INSERT INTO notes(value) VALUES ('persist')")
    report = backup_db.inspect_database(database)
    assert report["journal_mode"].lower() == "wal"
    assert report["integrity"] == "ok"


def test_restore_removes_stale_wal_sidecars(tmp_path):
    source = tmp_path / "backup.sqlite3"
    destination = tmp_path / "live.sqlite3"
    make_db(source, "restored-value")
    make_db(destination, "old-value")
    # Sidecars from the previous database must not be carried into the restore.
    Path(str(destination) + "-wal").write_bytes(b"stale wal data")
    Path(str(destination) + "-shm").write_bytes(b"stale shm data")

    backup_db.restore_database(source, destination)

    assert read_value(destination) == "restored-value"
    assert not Path(str(destination) + "-wal").exists()
    assert not Path(str(destination) + "-shm").exists()


def test_restore_keeps_safety_copy_before_sidecar_cleanup(tmp_path):
    source = tmp_path / "backup.sqlite3"
    destination = tmp_path / "live.sqlite3"
    make_db(source, "new")
    make_db(destination, "old")
    Path(str(destination) + "-wal").write_bytes(b"stale wal")

    safety_copy = backup_db.restore_database(source, destination)

    assert safety_copy is not None
    assert read_value(safety_copy) == "old"
    assert read_value(destination) == "new"


def test_diagnose_reports_missing_database_without_creating_it(tmp_path):
    database = tmp_path / "missing.sqlite3"
    report = backup_db.diagnose_database(database)
    assert report["exists"] is False
    assert report["integrity"] == "missing"
    assert report["parent_writable"] is True
    assert not database.exists()


def test_diagnose_reports_corrupt_database_without_modifying_it(tmp_path):
    database = tmp_path / "corrupt.sqlite3"
    database.write_bytes(b"not sqlite")
    before = database.read_bytes()
    report = backup_db.diagnose_database(database)
    assert report["exists"] is True
    assert report["integrity"] == "error"
    assert report["error"]
    assert database.read_bytes() == before


def test_restore_failure_restores_old_sidecars_and_database(tmp_path, monkeypatch):
    source = tmp_path / "backup.sqlite3"
    destination = tmp_path / "live.sqlite3"
    make_db(source, "new")
    make_db(destination, "old")
    wal = Path(str(destination) + "-wal")
    shm = Path(str(destination) + "-shm")
    wal.write_bytes(b"old wal bytes")
    shm.write_bytes(b"old shm bytes")
    # Keep the fixture sidecars byte-for-byte stable; a real backup connection
    # may legitimately create/update SQLite's shared-memory file.
    safety = tmp_path / "safety.sqlite3"
    make_db(safety, "old")
    monkeypatch.setattr(backup_db, "backup_database", lambda *args, **kwargs: safety)
    real_replace = backup_db.os.replace

    def failing_replace(src, dst):
        if str(dst) == str(destination) and str(src).endswith(".restore.tmp"):
            raise OSError("simulated replace failure")
        return real_replace(src, dst)

    monkeypatch.setattr(backup_db.os, "replace", failing_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        backup_db.restore_database(source, destination)
    assert wal.read_bytes() == b"old wal bytes"
    assert shm.read_bytes() == b"old shm bytes"
    assert read_value(destination) == "old"
    assert not list(tmp_path.glob(".*.restore.tmp"))
    assert not list(tmp_path.glob("*.pre-restore"))


def test_audit_backups_reports_valid_recent_and_corrupt_files(tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir()
    valid = directory / "good.sqlite3"
    corrupt = directory / "broken.sqlite3"
    make_db(valid, "safe")
    corrupt.write_bytes(b"not a sqlite database")

    report = backup_db.audit_backups(directory, max_age_days=7)

    assert report["directory_exists"] is True
    assert report["backup_count"] == 2
    assert report["valid_count"] == 1
    assert report["invalid_count"] == 1
    assert report["latest_valid"] == str(valid.resolve())
    assert report["has_recent_valid_backup"] is True
    assert next(item for item in report["backups"] if item["path"] == str(corrupt.resolve()))["valid"] is False


def test_audit_backups_detects_stale_backup_without_modifying_it(tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir()
    valid = directory / "old.sqlite3"
    make_db(valid, "old-but-valid")
    old_timestamp = 1_600_000_000
    import os
    os.utime(valid, (old_timestamp, old_timestamp))
    before = valid.read_bytes()

    report = backup_db.audit_backups(directory, max_age_days=7)

    assert report["valid_count"] == 1
    assert report["has_recent_valid_backup"] is False
    assert report["latest_valid_age_days"] > 7
    assert valid.read_bytes() == before


def test_audit_backups_missing_directory_is_non_destructive(tmp_path):
    directory = tmp_path / "missing-backups"
    report = backup_db.audit_backups(directory)
    assert report["directory_exists"] is False
    assert report["has_recent_valid_backup"] is False
    assert not directory.exists()


def test_audit_backups_rejects_negative_age(tmp_path):
    with pytest.raises(ValueError, match="negativo"):
        backup_db.audit_backups(tmp_path, max_age_days=-1)


def test_backup_writes_manifest_with_sha256_and_metadata(tmp_path):
    import hashlib
    import json

    source = tmp_path / "source.sqlite3"
    make_db(source, "manifest-test")
    backup = backup_db.backup_database(source, tmp_path / "backups")
    manifest_path = Path(str(backup) + ".json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["format_version"] == 1
    assert manifest["backup_file"] == backup.name
    assert manifest["integrity"] == "ok"
    assert manifest["size_bytes"] == backup.stat().st_size
    assert manifest["sha256"] == hashlib.sha256(backup.read_bytes()).hexdigest()
    assert manifest["table_count"] == 1


def test_audit_verifies_manifest_and_detects_changed_backup(tmp_path):
    source = tmp_path / "source.sqlite3"
    make_db(source, "original")
    backup = backup_db.backup_database(source, tmp_path / "backups")
    good = backup_db.audit_backups(backup.parent)
    assert good["manifest_verified_count"] == 1
    assert good["manifest_invalid_count"] == 0
    assert good["backups"][0]["checksum_verified"] is True

    with backup.open("ab") as stream:
        stream.write(b"tampered")
    bad = backup_db.audit_backups(backup.parent)
    assert bad["manifest_invalid_count"] == 1
    assert bad["has_recent_valid_backup"] is False
    assert bad["backups"][0]["manifest_status"] == "invalid"


def test_audit_reports_legacy_backup_without_manifest_as_compatible(tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir()
    legacy = directory / "legacy.sqlite3"
    make_db(legacy, "legacy")
    report = backup_db.audit_backups(directory)
    assert report["valid_count"] == 1
    assert report["legacy_without_manifest_count"] == 1
    assert report["has_recent_valid_backup"] is True


def test_audit_reports_corrupt_manifest_without_crashing(tmp_path):
    directory = tmp_path / "backups"
    directory.mkdir()
    backup = directory / "legacy.sqlite3"
    make_db(backup, "safe")
    Path(str(backup) + ".json").write_text("{broken", encoding="utf-8")
    report = backup_db.audit_backups(directory)
    assert report["manifest_invalid_count"] == 1
    assert report["backups"][0]["manifest_status"] == "invalid"
    assert report["has_recent_valid_backup"] is False


def test_append_audit_history_records_success_and_failure_without_database_contents(tmp_path):
    import json
    from datetime import datetime, timezone

    directory = tmp_path / "backups"
    directory.mkdir()
    backup = directory / "valid.sqlite3"
    make_db(backup, "private-content-not-in-history")
    report = backup_db.audit_backups(directory)
    history = tmp_path / "logs" / "audit.jsonl"
    fixed_now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

    backup_db.append_audit_history(history, report, now=fixed_now)
    missing_report = backup_db.audit_backups(tmp_path / "missing")
    backup_db.append_audit_history(history, missing_report, now=fixed_now)

    records = [json.loads(line) for line in history.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 2
    assert records[0]["status"] == "ok"
    assert records[0]["has_recent_valid_backup"] is True
    assert records[1]["status"] == "error"
    assert records[1]["directory_exists"] is False
    assert "private-content-not-in-history" not in history.read_text(encoding="utf-8")


def test_audit_history_appends_instead_of_overwriting(tmp_path):
    import json

    history = tmp_path / "audit.jsonl"
    report = backup_db.audit_backups(tmp_path / "missing")
    backup_db.append_audit_history(history, report)
    backup_db.append_audit_history(history, report)
    assert len(history.read_text(encoding="utf-8").splitlines()) == 2
    assert all(json.loads(line)["status"] == "error" for line in history.read_text(encoding="utf-8").splitlines())


def test_backup_policy_alerts_on_missing_history(tmp_path):
    report = backup_db.evaluate_backup_policy(tmp_path / "missing.jsonl")
    assert report["status"] == "alert"
    assert "history_missing" in {item["code"] for item in report["alerts"]}


def test_backup_policy_detects_consecutive_failures(tmp_path):
    import json
    from datetime import datetime, timezone

    history = tmp_path / "audit.jsonl"
    now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
    records = [
        {"recorded_at": "2026-10-28T11:00:00+00:00", "status": "ok", "has_recent_valid_backup": True, "invalid_count": 0, "manifest_invalid_count": 0},
        {"recorded_at": "2026-10-28T11:30:00+00:00", "status": "error", "has_recent_valid_backup": False, "invalid_count": 0, "manifest_invalid_count": 0},
        {"recorded_at": "2026-10-28T11:45:00+00:00", "status": "error", "has_recent_valid_backup": False, "invalid_count": 0, "manifest_invalid_count": 0},
    ]
    history.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    report = backup_db.evaluate_backup_policy(history, now=now)
    codes = {item["code"] for item in report["alerts"]}
    assert report["consecutive_failures"] == 2
    assert "consecutive_failures" in codes
    assert "no_recent_valid_backup" in codes


def test_backup_policy_warns_when_history_is_stale(tmp_path):
    import json
    from datetime import datetime, timezone

    history = tmp_path / "audit.jsonl"
    history.write_text(json.dumps({
        "recorded_at": "2026-10-27T00:00:00+00:00", "status": "ok",
        "has_recent_valid_backup": True, "invalid_count": 0, "manifest_invalid_count": 0,
    }) + "\n", encoding="utf-8")
    report = backup_db.evaluate_backup_policy(
        history, max_record_age_hours=24,
        now=datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc),
    )
    assert "history_stale" in {item["code"] for item in report["alerts"]}


def test_backup_policy_reports_malformed_lines_but_continues(tmp_path):
    import json

    history = tmp_path / "audit.jsonl"
    history.write_text("{bad json}\n" + json.dumps({
        "recorded_at": "2026-10-28T12:00:00+00:00", "status": "ok",
        "has_recent_valid_backup": True, "invalid_count": 0, "manifest_invalid_count": 0,
    }) + "\n", encoding="utf-8")
    report = backup_db.evaluate_backup_policy(history)
    assert report["record_count"] == 1
    assert "history_record_invalid" in {item["code"] for item in report["alerts"]}


def test_verify_restore_checks_isolated_copy_without_touching_live_database(tmp_path, monkeypatch):
    source = tmp_path / "backup.sqlite3"
    live = tmp_path / "live.sqlite3"
    make_db(source, "backup-value")
    make_db(live, "live-value")
    source_hash = backup_db._sha256_file(source)
    live_hash = backup_db._sha256_file(live)

    report = backup_db.verify_restore(source)

    assert report["status"] == "ok"
    assert report["active_database_touched"] is False
    assert report["backup_modified"] is False
    assert report["temporary_restore_removed"] is True
    assert report["table_count"] == 1
    assert read_value(live) == "live-value"
    assert backup_db._sha256_file(live) == live_hash
    assert backup_db._sha256_file(source) == source_hash


def test_verify_restore_rejects_corrupt_backup(tmp_path):
    corrupt = tmp_path / "corrupt.sqlite3"
    corrupt.write_bytes(b"not a sqlite database")
    with pytest.raises(sqlite3.DatabaseError):
        backup_db.verify_restore(corrupt)


def test_restore_rejects_backup_when_manifest_checksum_does_not_match(tmp_path):
    source = tmp_path / "backup.sqlite3"
    destination = tmp_path / "live.sqlite3"
    make_db(source, "trusted-data")
    make_db(destination, "must-survive")
    manifest_path = backup_db._write_backup_manifest(source, source)
    manifest = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sha256"] = "0" * 64
    manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="SHA-256"):
        backup_db.restore_database(source, destination)
    assert read_value(destination) == "must-survive"


def test_verify_restore_reports_manifest_checksum_verified(tmp_path):
    source = tmp_path / "backup.sqlite3"
    make_db(source, "verified-data")
    backup_db._write_backup_manifest(source, source)

    report = backup_db.verify_restore(source)

    assert report["status"] == "ok"
    assert report["manifest_status"] == "ok"
    assert report["checksum_verified"] is True
    assert report["active_database_touched"] is False


def test_verify_restore_rejects_tampered_manifest(tmp_path):
    source = tmp_path / "backup.sqlite3"
    make_db(source, "tampered-data")
    manifest_path = backup_db._write_backup_manifest(source, source)
    manifest = __import__("json").loads(manifest_path.read_text(encoding="utf-8"))
    manifest["size_bytes"] += 1
    manifest_path.write_text(__import__("json").dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="tamaño o SHA-256"):
        backup_db.verify_restore(source)


def test_restore_allows_legacy_backup_without_manifest(tmp_path):
    source = tmp_path / "legacy.sqlite3"
    destination = tmp_path / "live.sqlite3"
    make_db(source, "legacy-data")
    make_db(destination, "old-data")

    backup_db.restore_database(source, destination)

    assert read_value(destination) == "legacy-data"
