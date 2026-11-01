"""Banco de regresión reproducible para recuperación de memoria (v1.48).

Las etiquetas esperadas son juicio de prueba explícito, no verdad semántica universal.
Cada caso usa una cuenta aislada y valida métricas del endpoint supervisado.
"""
import base64
import hashlib
import hmac
import json
import time
import pytest
from fastapi.testclient import TestClient
import main


def _headers(account_id):
    main.inicializar_db()
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"memory-benchmark-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute(
            "INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)",
            (nonce, account_id, expires_at),
        )
    payload = json.dumps(
        {"exp": expires_at, "nonce": nonce, "account_id": account_id},
        separators=(",", ":"),
    ).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(
        hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    return {"Authorization": f"Bearer {body}.{signature}"}


CASES = [
    {
        "name": "direct_keyword_match",
        "query": "practicar inglés conversación",
        "relevant": "estudiar inglés y practicar conversación",
        "irrelevant": "receta sopa verduras",
        "expected_recall": 1.0,
    },
    {
        "name": "accent_normalization",
        "query": "alimentación saludable",
        "relevant": "consejos de alimentacion saludable",
        "irrelevant": "mantenimiento de bicicleta",
        "expected_recall": 1.0,
    },
    {
        "name": "project_relevance",
        "query": "proyecto construir aplicación",
        "relevant": "objetivo del proyecto construir aplicación web",
        "irrelevant": "historia del arte antiguo",
        "expected_recall": 1.0,
    },
    {
        "name": "irrelevant_query_does_not_claim_recall",
        "query": "planetas telescopio astronomía",
        "relevant": "observar planetas con telescopio y estudiar astronomía",
        "irrelevant": "receta sopa verduras",
        "expected_recall": 1.0,
    },
]


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_memory_retrieval_benchmark_cases(case):
    account = f"memory-benchmark-{case['name']}-{time.time_ns()}"
    expected_id = main.guardar_memoria(case["relevant"], "estudio", account_id=account)
    main.guardar_memoria(case["irrelevant"], "general", account_id=account)
    with TestClient(main.app) as client:
        response = client.post(
            "/memory/context-evaluate",
            headers=_headers(account),
            json={"query": case["query"], "expected_memory_ids": [expected_id], "limit": 8},
        )
    assert response.status_code == 200, case["name"]
    result = response.json()
    assert result["recall"] == case["expected_recall"], case["name"]
    assert expected_id not in result["missed_expected_ids"], case["name"]
    assert result["model_called"] is False
    assert result["history_saved"] is False
    assert result["automatic_changes"] is False


def test_memory_benchmark_does_not_retrieve_archived_memories():
    account = f"memory-benchmark-archived-{time.time_ns()}"
    memory_id = main.guardar_memoria("astronomía telescopio planetas", "estudio", account_id=account)
    with main.conectar_db() as conn:
        conn.execute("UPDATE memorias SET status='archived' WHERE id=? AND account_id=?", (memory_id, account))
    with TestClient(main.app) as client:
        response = client.post(
            "/memory/context-evaluate",
            headers=_headers(account),
            json={"query": "astronomía telescopio planetas", "expected_memory_ids": [memory_id]},
        )
    assert response.status_code == 200
    result = response.json()
    assert memory_id in result["missed_expected_ids"]
    assert result["recall"] == 0.0


def test_memory_benchmark_reports_zero_precision_when_no_memory_is_retrieved():
    account = f"memory-benchmark-empty-{time.time_ns()}"
    expected_id = main.guardar_memoria("biología celular mitocondrias", "estudio", account_id=account)
    with main.conectar_db() as conn:
        conn.execute("UPDATE memorias SET status='archived' WHERE id=? AND account_id=?", (expected_id, account))
    with TestClient(main.app) as client:
        response = client.post(
            "/memory/context-evaluate",
            headers=_headers(account),
            json={"query": "biología celular mitocondrias", "expected_memory_ids": [expected_id]},
        )
    assert response.status_code == 200
    result = response.json()
    assert result["retrieved_count"] == 0
    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0
