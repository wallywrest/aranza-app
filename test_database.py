"""Pruebas de respaldo, restauración e integridad SQLite de Aranza."""
import sqlite3
from contextlib import closing
from pathlib import Path

from backup_db import backup_database, integrity_check, restore_database


def create_db(path: Path, content: str):
    with closing(sqlite3.connect(path)) as conn:
        with conn:
            conn.execute("CREATE TABLE IF NOT EXISTS memorias (content TEXT NOT NULL)")
            conn.execute("INSERT INTO memorias(content) VALUES (?)", (content,))


def read_contents(path: Path):
    with closing(sqlite3.connect(path)) as conn:
        return [row[0] for row in conn.execute("SELECT content FROM memorias ORDER BY rowid")]


def test_backup_contains_committed_data_and_passes_integrity(tmp_path):
    source = tmp_path / "aranza.sqlite3"
    create_db(source, "recuerdo importante")
    backup = backup_database(source, tmp_path / "backups")
    assert backup.exists()
    assert read_contents(backup) == ["recuerdo importante"]
    integrity_check(backup)


def test_restore_preserves_old_database_as_safety_copy(tmp_path):
    current = tmp_path / "current.sqlite3"
    old_backup = tmp_path / "backup.sqlite3"
    create_db(current, "dato actual")
    create_db(old_backup, "dato del respaldo")

    safety_copy = restore_database(old_backup, current)

    assert safety_copy is not None and safety_copy.exists()
    assert read_contents(safety_copy) == ["dato actual"]
    assert read_contents(current) == ["dato del respaldo"]
    integrity_check(current)


def test_restore_refuses_to_restore_file_onto_itself(tmp_path):
    source = tmp_path / "same.sqlite3"
    create_db(source, "dato")
    try:
        restore_database(source, source)
    except ValueError as exc:
        assert "no puede ser" in str(exc)
    else:
        raise AssertionError("Debió rechazar restaurar una base sobre sí misma")
