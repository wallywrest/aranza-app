"""Protege el arranque si desaparece una base previamente inicializada."""
from pathlib import Path

import pytest

import main


def test_first_start_allows_database_creation_and_returns_marker(tmp_path, monkeypatch):
    db = tmp_path / "aranza.sqlite3"
    marker = main.verificar_estado_almacenamiento(db, require_persistent=True)
    assert marker == tmp_path / ".aranza.sqlite3.initialized"
    assert not db.exists()
    monkeypatch.setattr(main, "DATABASE_PATH", str(db))
    main.registrar_almacenamiento_inicializado(marker)
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8") == str(db.resolve())


def test_missing_database_after_marker_fails_closed(tmp_path):
    db = tmp_path / "aranza.sqlite3"
    marker = tmp_path / ".aranza.sqlite3.initialized"
    marker.write_text(str(db.resolve()), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Se detiene el arranque"):
        main.verificar_estado_almacenamiento(db, require_persistent=True)


def test_existing_database_with_marker_is_allowed(tmp_path):
    db = tmp_path / "aranza.sqlite3"
    db.write_bytes(b"existing database placeholder")
    marker = tmp_path / ".aranza.sqlite3.initialized"
    marker.write_text(str(db.resolve()), encoding="utf-8")
    assert main.verificar_estado_almacenamiento(db, require_persistent=True) == marker


def test_guard_is_inert_when_persistent_storage_requirement_is_disabled(tmp_path):
    db = tmp_path / "missing.sqlite3"
    marker = tmp_path / ".missing.sqlite3.initialized"
    marker.write_text("previous install", encoding="utf-8")
    assert main.verificar_estado_almacenamiento(db, require_persistent=False) is None


def test_guard_rejects_missing_storage_directory(tmp_path):
    db = tmp_path / "missing-dir" / "aranza.sqlite3"
    with pytest.raises(RuntimeError, match="directorio de almacenamiento"):
        main.verificar_estado_almacenamiento(db, require_persistent=True)
