"""Pruebas de la revisión heurística de vigencia de recuerdos."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def _token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"audit-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at) VALUES (?, ?)", (nonce, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_audit_flags_temporal_language_without_claiming_staleness():
    memories = [
        {"id": 1, "category": "goal", "content": "Antes quería estudiar medicina"},
        {"id": 2, "category": "general", "content": "Me gusta el café"},
    ]
    results = main.auditar_memorias_desactualizadas(memories)
    assert len(results) == 1
    assert results[0]["id"] == 1
    assert "no confirma" not in results[0]["reason"]  # reason asks for review, not a verdict


def test_audit_is_bounded_and_empty_input_is_empty():
    assert main.auditar_memorias_desactualizadas([], limite=20) == []
    memories = [{"id": i, "content": "Actualmente estoy estudiando"} for i in range(60)]
    assert len(main.auditar_memorias_desactualizadas(memories, limite=100)) == 50


def test_memory_audit_requires_authentication():
    with TestClient(main.app) as client:
        response = client.get("/memory/audit")
    assert response.status_code == 401


def test_memory_audit_endpoint_is_read_only_and_authenticated():
    with TestClient(main.app) as client:
        response = client.get("/memory/audit", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 200
    assert response.json()["automatic_changes"] is False
