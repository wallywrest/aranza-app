"""Pruebas de actualización segura de recuerdos."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"update-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at) VALUES (?, ?)", (nonce, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_update_memory_changes_content_and_category_for_owner():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Meta antigua", "general", account_id="owner")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.put(f"/memory/{memory_id}", json={"content": "Meta actualizada", "category": "goal"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["updated"] is True
    memories = main.obtener_memorias(account_id="owner")
    saved = next(item for item in memories if item["id"] == memory_id)
    assert saved["content"] == "Meta actualizada"
    assert saved["category"] == "goal"


def test_update_memory_cannot_change_another_accounts_memory():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Privado", "general", account_id="other")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.put(f"/memory/{memory_id}", json={"content": "Modificado", "category": "general"}, headers=headers)
    assert response.status_code == 404
    other_memories = main.obtener_memorias(account_id="other")
    assert next(item for item in other_memories if item["id"] == memory_id)["content"] == "Privado"


def test_update_memory_requires_authentication():
    with TestClient(main.app) as client:
        response = client.put("/memory/1", json={"content": "Texto", "category": "general"})
    assert response.status_code == 401
