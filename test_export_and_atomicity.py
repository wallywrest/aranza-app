"""Pruebas de exportación protegida y guardado transaccional."""
import json
import sys
from uuid import uuid4
import types

_groq = types.ModuleType("groq")
class _UnusedAsyncGroq:
    def __init__(self, *args, **kwargs):
        pass
_groq.AsyncGroq = _UnusedAsyncGroq
sys.modules.setdefault("groq", _groq)

import main
from fastapi.testclient import TestClient


def test_export_requires_authentication():
    with TestClient(main.app) as client:
        response = client.get("/export")
        assert response.status_code == 401


def test_authenticated_export_contains_messages_and_memories():
    main.guardar_intercambio("chat_export_test", "hola", "qué tal")
    memory_id = main.guardar_memoria("prefiere respuestas en español", "preferencia")
    saved_memory = next(item for item in main.obtener_memorias() if item["id"] == memory_id)
    assert saved_memory["category"] == "preferencia"
    assert saved_memory["content"] == "prefiere respuestas en español"
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        response = client.get("/export", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "attachment; filename=\"aranza-export.json\"" == response.headers.get("content-disposition")
    data = response.json()
    assert data["format"] == "aranza-export-v3"
    assert "conversation_metadata" in data
    assert "memory_history" in data
    assert "memory_review_decisions" in data
    assert "profile" in data
    assert "investigations" in data
    assert "investigation_relations" in data
    assert "investigation_history" in data
    assert any(item["content"] == "hola" for item in data["conversations"])
    assert any(item["content"] == "prefiere respuestas en español" for item in data["memories"])


def test_exchange_is_saved_as_two_ordered_rows():
    conversation_id = "chat_atomic_test"
    main.borrar_conversacion(conversation_id)
    main.guardar_intercambio(conversation_id, "pregunta", "respuesta")
    rows = main.obtener_historial_completo(conversation_id)
    assert rows == [
        {"role": "user", "content": "pregunta"},
        {"role": "assistant", "content": "respuesta"},
    ]


def test_delete_personal_data_requires_confirmation_and_password():
    main.inicializar_db()
    suffix = uuid4().hex
    account_id = f"delete-test-{suffix}"
    username = f"delete-{suffix[:16]}"
    password = f"synthetic-password-{suffix[:12]}"
    salt, digest = main.generar_hash_contrasena(password)
    with main.conectar_db() as conn:
        conn.execute(
            """INSERT INTO cuentas(account_id, username, password_salt, password_hash, password_iterations)
               VALUES(?, ?, ?, ?, ?)""",
            (account_id, username, salt, digest, main.PASSWORD_HASH_ITERATIONS),
        )
    conversation_id = f"chat-privacy-delete-{suffix}"
    main.guardar_intercambio(conversation_id, "synthetic private data", "synthetic private answer", account_id=account_id)
    main.guardar_memoria("synthetic memory to delete", "general", account_id=account_id)
    main.guardar_perfil_cuenta(account_id, {"comunicacion_observada": ["synthetic profile to delete"]})

    with TestClient(main.app) as client:
        login = client.post("/login", json={"username": username, "password": password})
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        bad_phrase = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": password, "confirmation": "borrar todo"
        })
        assert bad_phrase.status_code == 400
        bad_password = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": "incorrecta", "confirmation": "ELIMINAR MIS DATOS"
        })
        assert bad_password.status_code == 403
        deleted = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": password, "confirmation": "ELIMINAR MIS DATOS"
        })
        assert deleted.status_code == 200
        assert deleted.json()["account_preserved"] is True
        assert deleted.json()["deleted_counts"]["profile_reset"] == 1
        assert client.get("/export", headers=headers).status_code == 401
        new_login = client.post("/login", json={"username": username, "password": password})
        assert new_login.status_code == 200
        new_headers = {"Authorization": f"Bearer {new_login.json()['access_token']}"}
        main.inicializar_db()
        exported = client.get("/export", headers=new_headers).json()

    assert not any(row["conversation_id"] == conversation_id for row in exported["conversations"])
    assert not any(row["content"] == "synthetic memory to delete" for row in exported["memories"])
    assert all(values == [] for values in exported["profile"].values())

def test_export_includes_account_profile_research_and_memory_state_without_credentials():
    main.inicializar_db()
    suffix = uuid4().hex
    account_id = f"export-test-{suffix}"
    username = f"export-{suffix[:16]}"
    password = "synthetic-test-password"
    salt, digest = main.generar_hash_contrasena(password)
    with main.conectar_db() as conn:
        conn.execute(
            """INSERT INTO cuentas(account_id, username, password_salt, password_hash, password_iterations)
               VALUES(?, ?, ?, ?, ?)""",
            (account_id, username, salt, digest, main.PASSWORD_HASH_ITERATIONS),
        )

    conversation_id = f"export-conversation-{suffix}"
    main.guardar_intercambio(conversation_id, "synthetic question", "synthetic answer", account_id=account_id)
    main.guardar_perfil_cuenta(account_id, {
        "comunicacion_observada": ["synthetic profile marker"],
    })
    memory_id = main.guardar_memoria("synthetic memory marker", "test", account_id=account_id)
    own_research_id = f"research-own-{suffix}"
    related_research_id = f"research-related-{suffix}"
    foreign_research_id = f"research-other-{suffix}"
    with main.conectar_db() as conn:
        conn.execute(
            "INSERT INTO memoria_historial(memory_id, account_id, category, content) VALUES (?, ?, ?, ?)",
            (memory_id, account_id, "test", "synthetic prior memory"),
        )
        conn.execute(
            "INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
            (account_id, memory_id, "temporal", "synthetic candidate"),
        )
        for research_id, research_account in (
            (own_research_id, account_id),
            (related_research_id, account_id),
            (foreign_research_id, f"other-{suffix}"),
        ):
            conn.execute(
                """INSERT INTO investigaciones
                   (id, account_id, conversation_id, title, query, summary, sources_json, evidence_json, tags_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    research_id, research_account, conversation_id if research_account == account_id else None,
                    "synthetic title", "synthetic query", "synthetic summary",
                    json.dumps([{"url": "https://example.test/source", "title": "synthetic source"}]),
                    json.dumps({"claim": "synthetic evidence"}),
                    json.dumps(["synthetic-tag"]),
                ),
            )
        conn.execute(
            "INSERT INTO relaciones_investigacion(account_id, research_id, related_id) VALUES (?, ?, ?)",
            (account_id, own_research_id, related_research_id),
        )
        conn.execute(
            "INSERT INTO historial_investigacion(account_id, research_id, snapshot_json) VALUES (?, ?, ?)",
            (account_id, own_research_id, json.dumps({"title": "synthetic prior title"})),
        )

    token = main.crear_token_sesion(account_id)
    with TestClient(main.app) as client:
        response = client.get("/export", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "aranza-export-v3"
    assert data["account"] == {"username": username}
    assert data["profile"]["comunicacion_observada"] == ["synthetic profile marker"]
    assert any(item["id"] == memory_id and item["status"] == "active" for item in data["memories"])
    assert data["memory_history"][0]["content"] == "synthetic prior memory"
    assert data["memory_review_decisions"][0]["candidate_content"] == "synthetic candidate"
    exported = {item["id"]: item for item in data["investigations"]}
    assert set(exported) == {own_research_id, related_research_id}
    assert exported[own_research_id]["sources"][0]["title"] == "synthetic source"
    assert exported[own_research_id]["evidence"]["claim"] == "synthetic evidence"
    assert exported[own_research_id]["tags"] == ["synthetic-tag"]
    assert data["investigation_relations"][0]["related_id"] == related_research_id
    assert data["investigation_history"][0]["snapshot"]["title"] == "synthetic prior title"
    encoded = json.dumps(data)
    assert foreign_research_id not in encoded
    assert "password_hash" not in encoded
    assert "password_salt" not in encoded
    assert digest not in encoded
