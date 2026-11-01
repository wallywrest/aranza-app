"""Pruebas de aislamiento de datos por cuenta y migración no destructiva."""
import base64
import hashlib
import hmac
import json
import time
import sqlite3

import main
from fastapi.testclient import TestClient


def _token_for_account(account_id: str) -> str:
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"test-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at) VALUES (?, ?)", (nonce, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_account_scope_separates_conversations_and_memories():
    main.inicializar_db()
    conversation_id = "shared-looking-id"
    main.guardar_intercambio(conversation_id, "dato de owner", "respuesta owner", account_id="owner")
    main.guardar_intercambio(conversation_id, "dato privado de otra cuenta", "respuesta privada", account_id="other-account")
    main.guardar_memoria("recuerdo owner", "test", account_id="owner")
    main.guardar_memoria("recuerdo privado", "test", account_id="other-account")

    assert main.obtener_historial_completo(conversation_id, account_id="owner") == [
        {"role": "user", "content": "dato de owner"},
        {"role": "assistant", "content": "respuesta owner"},
    ]
    assert main.obtener_historial_completo(conversation_id, account_id="other-account")[0]["content"] == "dato privado de otra cuenta"
    assert [m["content"] for m in main.obtener_memorias(account_id="owner")] == ["recuerdo owner"]


def test_authenticated_account_cannot_read_or_delete_other_account_conversation():
    main.inicializar_db()
    conversation_id = "isolated-route-test"
    main.guardar_intercambio(conversation_id, "secreto de otra cuenta", "respuesta privada", account_id="other-account")
    token = _token_for_account("owner")
    headers = {"Authorization": f"Bearer {token}"}
    with TestClient(main.app) as client:
        read = client.get(f"/conversations/{conversation_id}/messages", headers=headers)
        delete = client.delete(f"/conversations/{conversation_id}", headers=headers)
    assert read.status_code == 200 and read.json()["messages"] == []
    assert delete.status_code == 404
    assert main.obtener_historial_completo(conversation_id, account_id="other-account")[0]["content"] == "secreto de otra cuenta"


def test_legacy_schema_migrates_without_losing_rows(tmp_path, monkeypatch):
    legacy_db = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(legacy_db) as conn:
        conn.execute("CREATE TABLE mensajes (id INTEGER PRIMARY KEY, conversation_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("INSERT INTO mensajes(conversation_id, role, content) VALUES ('old-chat', 'user', 'preservar esto')")
        conn.execute("CREATE TABLE memorias (id INTEGER PRIMARY KEY, category TEXT NOT NULL DEFAULT 'general', content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("INSERT INTO memorias(category, content) VALUES ('nota', 'recuerdo antiguo')")
    monkeypatch.setattr(main, "DATABASE_PATH", str(legacy_db))
    main.inicializar_db()
    with sqlite3.connect(legacy_db) as conn:
        message = conn.execute("SELECT account_id, content FROM mensajes WHERE conversation_id='old-chat'").fetchone()
        memory = conn.execute("SELECT account_id, category, content FROM memorias").fetchone()
    assert message == ("owner", "preservar esto")
    assert memory == ("owner", "nota", "recuerdo antiguo")
