"""Pruebas de persistencia de la inicialización de SQLite entre reinicios."""
import sqlite3

import main


def test_database_initialization_is_idempotent_and_preserves_user_data(tmp_path, monkeypatch):
    database = tmp_path / "aranza.sqlite3"
    monkeypatch.setattr(main, "DATABASE_PATH", str(database))
    monkeypatch.setattr(main, "ARANZA_PASSWORD", "")

    main.inicializar_db()
    with main.conectar_db() as conn:
        conn.execute(
            "INSERT INTO mensajes(conversation_id, account_id, role, content) VALUES (?, ?, ?, ?)",
            ("restart-test", "account-a", "user", "mensaje que debe sobrevivir")
        )
        conn.execute(
            "INSERT INTO memorias(account_id, category, content) VALUES (?, ?, ?)",
            ("account-a", "general", "memoria persistente")
        )

    # Simula la inicialización del proceso tras un reinicio.
    main.inicializar_db()
    with main.conectar_db() as conn:
        message = conn.execute(
            "SELECT content FROM mensajes WHERE conversation_id = ? AND account_id = ?",
            ("restart-test", "account-a")
        ).fetchone()
        memory = conn.execute(
            "SELECT content FROM memorias WHERE account_id = ?", ("account-a",)
        ).fetchone()
        assert message["content"] == "mensaje que debe sobrevivir"
        assert memory["content"] == "memoria persistente"
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_database_file_remains_readable_after_connection_reopens(tmp_path, monkeypatch):
    database = tmp_path / "reopen.sqlite3"
    monkeypatch.setattr(main, "DATABASE_PATH", str(database))
    monkeypatch.setattr(main, "ARANZA_PASSWORD", "")
    main.inicializar_db()
    with main.conectar_db() as conn:
        conn.execute(
            "INSERT INTO mensajes(conversation_id, account_id, role, content) VALUES (?, ?, ?, ?)",
            ("reopen", "account-b", "assistant", "respuesta guardada")
        )
    # A fresh SQLite connection represents a later request or process.
    with sqlite3.connect(database) as conn:
        row = conn.execute(
            "SELECT content FROM mensajes WHERE conversation_id = ?", ("reopen",)
        ).fetchone()
    assert row == ("respuesta guardada",)
