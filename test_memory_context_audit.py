"""Pruebas de auditoría heurística del contexto recuperado."""
import base64
import hashlib
import hmac
import json
import time
from fastapi.testclient import TestClient
import main


def _headers(account_id="context-audit-owner"):
    main.inicializar_db()
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"context-audit-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)", (nonce, account_id, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return {"Authorization": f"Bearer {body}.{signature}"}


def test_context_audit_reports_coverage_without_side_effects():
    main.inicializar_db()
    account = "context-audit-owner"
    memory_id = main.guardar_memoria("estudio inglés conversación semanal", "proyectos", account_id=account)
    before = len(main.obtener_historial("audit-chat", account))
    with TestClient(main.app) as client:
        response = client.get("/memory/context-audit", params={"query": "practicar inglés conversación", "limit": 8}, headers=_headers(account))
    assert response.status_code == 200
    data = response.json()
    assert data["selected_count"] >= 1
    assert data["matched_keyword_count"] >= 1
    assert 0 <= data["lexical_coverage"] <= 1
    assert data["automatic_changes"] is False
    assert data["model_called"] is False
    assert data["history_saved"] is False
    assert len(main.obtener_historial("audit-chat", account)) == before
    assert memory_id in [m["id"] for m in main.obtener_memorias(limite=500, account_id=account)]


def test_context_audit_is_account_scoped():
    main.inicializar_db()
    main.guardar_memoria("secreto privado astrofisica exclusivo", "personal", account_id="audit-private")
    with TestClient(main.app) as client:
        response = client.get("/memory/context-audit", params={"query": "secreto astrofisica exclusivo"}, headers=_headers("audit-other"))
    assert response.status_code == 200
    assert response.json()["selected_count"] == 0


def test_context_audit_validates_query_and_bounds_limit():
    with TestClient(main.app) as client:
        empty = client.get("/memory/context-audit", params={"query": "   "}, headers=_headers())
        long = client.get("/memory/context-audit", params={"query": "x" * 4001}, headers=_headers())
        bounded = client.get("/memory/context-audit", params={"query": "inglés", "limit": 999}, headers=_headers())
    assert empty.status_code == 422
    assert long.status_code == 422
    assert bounded.status_code == 200
    assert bounded.json()["limit"] == 20
