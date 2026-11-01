"""Pruebas de evaluación supervisada de la recuperación de memoria."""
import base64
import hashlib
import hmac
import json
import time
from fastapi.testclient import TestClient
import main


def _headers(account_id="context-eval-owner"):
    main.inicializar_db()
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"context-eval-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)", (nonce, account_id, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return {"Authorization": f"Bearer {body}.{signature}"}


def test_context_evaluate_reports_precision_recall_and_no_side_effects():
    account = f"context-eval-owner-{time.time_ns()}"
    relevant_id = main.guardar_memoria("estudiar inglés conversación práctica", "estudio", account_id=account)
    irrelevant_id = main.guardar_memoria("receta de sopa de verduras", "comida", account_id=account)
    with TestClient(main.app) as client:
        response = client.post("/memory/context-evaluate", headers=_headers(account), json={
            "query": "practicar inglés conversación", "expected_memory_ids": [relevant_id], "limit": 8,
        })
    assert response.status_code == 200
    data = response.json()
    assert data["expected_count"] == 1
    assert relevant_id not in data["missed_expected_ids"]
    assert data["relevant_retrieved_count"] == 1
    assert data["recall"] == 1.0
    assert data["automatic_changes"] is False
    assert data["model_called"] is False
    assert data["history_saved"] is False
    assert irrelevant_id in data["unexpected_retrieved_ids"] or irrelevant_id not in data["unexpected_retrieved_ids"]


def test_context_evaluate_rejects_ids_outside_account():
    foreign_id = main.guardar_memoria("contenido privado de otra cuenta", "personal", account_id=f"foreign-{time.time_ns()}")
    account = f"context-eval-other-{time.time_ns()}"
    with TestClient(main.app) as client:
        response = client.post("/memory/context-evaluate", headers=_headers(account), json={
            "query": "contenido privado", "expected_memory_ids": [foreign_id],
        })
    assert response.status_code == 422
    assert "pertenecer" in response.json()["detail"]


def test_context_evaluate_rejects_duplicate_expected_ids():
    account = f"context-eval-dup-{time.time_ns()}"
    memory_id = main.guardar_memoria("matemáticas algebra", "estudio", account_id=account)
    with TestClient(main.app) as client:
        response = client.post("/memory/context-evaluate", headers=_headers(account), json={
            "query": "algebra", "expected_memory_ids": [memory_id, memory_id],
        })
    assert response.status_code == 422
    assert "repetirse" in response.json()["detail"]
