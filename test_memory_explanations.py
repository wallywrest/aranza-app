"""Pruebas para explicaciones transparentes de la selección de memoria."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def _token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"explain-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at) VALUES (?, ?)", (nonce, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_explanation_marks_selected_and_lists_matching_terms():
    memories = [
        {"id": 1, "category": "proyectos", "content": "Estoy aprendiendo Excel para la universidad"},
        {"id": 2, "category": "general", "content": "Tengo un gato naranja"},
    ]
    selected = main.seleccionar_memorias_relevantes("Ayúdame con Excel universidad", memories, limite=1)
    explanations = main.explicar_seleccion_memorias("Ayúdame con Excel universidad", memories, selected)
    chosen = next(item for item in explanations if item["id"] == 1)
    omitted = next(item for item in explanations if item["id"] == 2)
    assert chosen["selected"] is True
    assert "excel" in chosen["matched_terms"]
    assert omitted["selected"] is False
    assert omitted["reason"]


def test_preview_explanations_are_account_scoped_and_authenticated():
    main.inicializar_db()
    main.guardar_memoria("Mi proyecto es aprender Excel", "proyectos", account_id="owner")
    main.guardar_memoria("Dato privado de otra cuenta sobre Excel", "general", account_id="other")
    headers = {"Authorization": f"Bearer {_token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/preview", json={"query": "Ayúdame con Excel", "limit": 5}, headers=headers)
        unauthenticated = client.post("/memory/preview", json={"query": "Excel", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["explanations"]
    assert all("otra cuenta" not in item["content"] for item in data["explanations"])
    assert unauthenticated.status_code == 401
