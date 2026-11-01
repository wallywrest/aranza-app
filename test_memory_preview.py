"""Pruebas de vista previa segura del contexto de memoria."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def _token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"preview-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at) VALUES (?, ?)", (nonce, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_memory_preview_requires_authentication():
    with TestClient(main.app) as client:
        response = client.post("/memory/preview", json={"query": "Excel"})
    assert response.status_code == 401


def test_memory_preview_returns_relevant_account_memories_without_mutating_them():
    main.inicializar_db()
    main.guardar_memoria("Mi proyecto es aprender Excel", "proyectos", account_id="owner")
    main.guardar_memoria("Dato privado de otra cuenta sobre Excel", "general", account_id="other")
    before = main.obtener_memorias(account_id="owner")
    headers = {"Authorization": f"Bearer {_token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/preview", json={"query": "Ayúdame con Excel", "limit": 5}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["selected_count"] >= 1
    assert all("otra cuenta" not in item["content"] for item in data["memories"])
    assert main.obtener_memorias(account_id="owner") == before


def test_memory_preview_validates_query_and_limit():
    headers = {"Authorization": f"Bearer {_token('owner')}"}
    with TestClient(main.app) as client:
        empty_query = client.post("/memory/preview", json={"query": ""}, headers=headers)
        invalid_limit = client.post("/memory/preview", json={"query": "Excel", "limit": 99}, headers=headers)
    assert empty_query.status_code == 422
    assert invalid_limit.status_code == 422
