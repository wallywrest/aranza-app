"""Tests de la previsualización explicable de contexto de memoria."""
import base64
import hashlib
import hmac
import json
import time
from fastapi.testclient import TestClient
import main


def _token(account_id="context-preview-owner"):
    main.inicializar_db()
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"context-preview-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)", (nonce, account_id, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def _headers(account_id="context-preview-owner"):
    return {"Authorization": f"Bearer {_token(account_id)}"}


def test_context_preview_explains_matches_and_has_no_side_effects():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Estoy estudiando inglés para mejorar conversación", "proyectos", account_id="context-preview-owner")
    before = len(main.obtener_historial("preview-conversation", "context-preview-owner"))
    with TestClient(main.app) as client:
        response = client.get("/memory/context-preview", params={"query": "quiero practicar inglés conversación", "limit": 8}, headers=_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["model_called"] is False
    assert data["history_saved"] is False
    assert data["automatic_changes"] is False
    assert any(item["id"] == memory_id and "ingles" in item["matched_terms"] for item in data["memories"])
    assert len(main.obtener_historial("preview-conversation", "context-preview-owner")) == before


def test_context_preview_is_account_scoped():
    main.inicializar_db()
    main.guardar_memoria("secreto de contexto exclusivo", "personal", account_id="context-preview-private")
    with TestClient(main.app) as client:
        response = client.get("/memory/context-preview", params={"query": "secreto contexto exclusivo"}, headers=_headers("context-preview-other"))
    assert response.status_code == 200
    assert all("exclusivo" not in item["content"] for item in response.json()["memories"])


def test_context_preview_validates_query_and_clamps_limit():
    with TestClient(main.app) as client:
        empty = client.get("/memory/context-preview", params={"query": "   "}, headers=_headers())
        long = client.get("/memory/context-preview", params={"query": "x" * 4001}, headers=_headers())
        bounded = client.get("/memory/context-preview", params={"query": "inglés", "limit": 999}, headers=_headers())
    assert empty.status_code == 422
    assert long.status_code == 422
    assert bounded.status_code == 200
    assert bounded.json()["limit"] == 20
