"""Pruebas para el registro persistente de decisiones de revisión de memoria."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"review-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at, account_id) VALUES (?, ?, ?)", (nonce, expires_at, account_id))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_review_decision_requires_authentication():
    with TestClient(main.app) as client:
        response = client.post("/memory/review-decision", json={"memory_id": 1, "decision": "temporal", "candidate_content": "texto"})
    assert response.status_code == 401


def test_review_decision_persists_and_is_listed_for_own_account():
    main.inicializar_db()
    memory_id = main.guardar_memoria(f"review-test-{time.time_ns()}", "general", account_id="owner")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        saved = client.post("/memory/review-decision", json={"memory_id": memory_id, "decision": "temporal", "candidate_content": "versión nueva"}, headers=headers)
        listed = client.get("/memory/review-decisions", headers=headers)
    assert saved.status_code == 200
    assert saved.json()["saved"] is True
    assert any(row["id"] == saved.json()["id"] and row["decision"] == "temporal" for row in listed.json()["decisions"])


def test_review_decision_cannot_reference_another_accounts_memory():
    main.inicializar_db()
    memory_id = main.guardar_memoria(f"other-review-test-{time.time_ns()}", "general", account_id="different-account")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/review-decision", json={"memory_id": memory_id, "decision": "no_contradiccion", "candidate_content": "texto"}, headers=headers)
    assert response.status_code == 404


def test_review_decision_rejects_unknown_decision():
    main.inicializar_db()
    memory_id = main.guardar_memoria(f"bad-review-test-{time.time_ns()}", "general", account_id="owner")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/review-decision", json={"memory_id": memory_id, "decision": "inventada", "candidate_content": "texto"}, headers=headers)
    assert response.status_code == 422
