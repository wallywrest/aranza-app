"""Pruebas para archivar y reactivar recuerdos sin borrarlos."""
import base64
import hashlib
import hmac
import json
import time
from fastapi.testclient import TestClient
import main


def _headers(account_id="owner"):
    exp = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"archive-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at, account_id) VALUES (?, ?, ?)", (nonce, exp, account_id))
    payload = json.dumps({"exp": exp, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return {"Authorization": f"Bearer {body}.{sig}"}


def test_archived_memory_is_not_selected_as_context_and_can_be_reactivated():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Prefiero respuestas breves sobre Excel", "preference", account_id="owner")
    with TestClient(main.app) as client:
        response = client.post(f"/memory/{memory_id}/archive", json={"status": "archived"}, headers=_headers())
        assert response.status_code == 200
        memories = main.obtener_memorias(account_id="owner")
        assert next(m for m in memories if m["id"] == memory_id)["status"] == "archived"
        assert all(m["id"] != memory_id for m in main.seleccionar_memorias_relevantes("Excel respuestas", memories))
        assert client.post(f"/memory/{memory_id}/archive", json={"status": "active"}, headers=_headers()).status_code == 200
        memories = main.obtener_memorias(account_id="owner")
        assert next(m for m in memories if m["id"] == memory_id)["status"] == "active"
        assert any(m["id"] == memory_id for m in main.seleccionar_memorias_relevantes("Excel respuestas", memories))


def test_archive_requires_auth_and_cannot_change_other_account_memory():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Recuerdo privado", "general", account_id="other")
    with TestClient(main.app) as client:
        assert client.post(f"/memory/{memory_id}/archive", json={"status": "archived"}).status_code == 401
        assert client.post(f"/memory/{memory_id}/archive", json={"status": "archived"}, headers=_headers("owner")).status_code == 404


def test_archive_rejects_unknown_status():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Recuerdo", "general", account_id="owner")
    with TestClient(main.app) as client:
        assert client.post(f"/memory/{memory_id}/archive", json={"status": "deleted"}, headers=_headers()).status_code == 422
