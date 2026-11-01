"""Pruebas para relaciones heurísticas entre recuerdos."""
import base64
import hashlib
import hmac
import json
import time
from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"relations-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)", (nonce, account_id, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def headers(account_id="owner"):
    return {"Authorization": f"Bearer {token(account_id)}"}


def test_relations_detect_related_memories_without_changing_them():
    main.inicializar_db()
    a = main.guardar_memoria("Me gusta estudiar inglés y practicar conversación", "preferencias", account_id="owner")
    b = main.guardar_memoria("Me gusta estudiar inglés y practicar conversación cada semana", "preferencias", account_id="owner")
    with TestClient(main.app) as client:
        response = client.get("/memory/relations", headers=headers())
        current = client.get("/memory", headers=headers())
    assert response.status_code == 200
    data = response.json()
    assert any({r["memory_a"]["id"], r["memory_b"]["id"]} == {a, b} for r in data["relations"])
    assert data["automatic_changes"] is False
    assert any(m["id"] == a for m in current.json()["memories"])
    assert any(m["id"] == b for m in current.json()["memories"])


def test_relations_are_account_scoped():
    main.inicializar_db()
    main.guardar_memoria("Privado: me gusta estudiar inglés y practicar conversación", "preferencias", account_id="relations-private")
    main.guardar_memoria("Privado: me gusta estudiar inglés y practicar conversación a diario", "preferencias", account_id="relations-private")
    with TestClient(main.app) as client:
        response = client.get("/memory/relations", headers=headers("relations-other"))
    assert response.status_code == 200
    assert response.json()["memory_count"] == 0
    assert response.json()["relations"] == []


def test_relations_limit_is_clamped():
    main.inicializar_db()
    with TestClient(main.app) as client:
        response = client.get("/memory/relations?limit=9999", headers=headers())
    assert response.status_code == 200
    assert response.json()["limit"] == 200
