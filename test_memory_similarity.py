"""Pruebas de detección conservadora de recuerdos parecidos."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"similarity-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, expires_at) VALUES (?, ?)", (nonce, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def test_similarity_detects_near_duplicate_without_mutating_memory():
    memories = [{"id": 3, "category": "metas", "content": "Mi meta es estudiar ingeniería industrial en TESE"}]
    found = main.analizar_memorias_similares("Mi meta es estudiar ingeniería industrial en el TESE", "metas", memories)
    assert found
    assert found[0]["id"] == 3
    assert found[0]["review_type"] == "posible_duplicado"
    assert memories[0]["content"] == "Mi meta es estudiar ingeniería industrial en TESE"


def test_similarity_returns_empty_for_unrelated_memory():
    memories = [{"id": 4, "category": "general", "content": "Me gusta escuchar jazz por la noche"}]
    assert main.analizar_memorias_similares("Estoy aprendiendo Excel para mi trabajo", "proyectos", memories) == []


def test_memory_check_requires_authentication():
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Meta de estudiar", "category": "metas"})
    assert response.status_code == 401


def test_memory_check_is_scoped_to_authenticated_account():
    main.inicializar_db()
    main.guardar_memoria("Mi meta es estudiar ingeniería industrial en TESE", "metas", account_id="other")
    headers = {"Authorization": f"Bearer {token('owner')}"}
    with TestClient(main.app) as client:
        response = client.post("/memory/check", json={"content": "Mi meta es estudiar ingeniería industrial en TESE", "category": "metas"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["candidate_count"] == 0
    assert response.json()["automatic_changes"] is False


def test_similarity_flags_explicit_opposite_preference_as_possible_contradiction():
    memories = [{"id": 8, "category": "preference", "content": "Me gusta escuchar jazz por la noche"}]
    found = main.analizar_memorias_similares("No me gusta escuchar jazz por la noche", "preference", memories)
    assert found
    assert found[0]["review_type"] == "posible_contradiccion"
    assert "revisa manualmente" in found[0]["review_note"]


def test_similarity_does_not_infer_contradiction_from_unrelated_topics():
    memories = [{"id": 9, "category": "preference", "content": "No me gusta el café"}]
    found = main.analizar_memorias_similares("Me gusta estudiar ingeniería", "preference", memories)
    assert found == []
