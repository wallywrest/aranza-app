"""Pruebas de exportación protegida y guardado transaccional."""
import sys
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
    assert data["format"] == "aranza-export-v2"
    assert "conversation_metadata" in data
    assert "memory_history" in data
    assert "memory_review_decisions" in data
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
    main.guardar_intercambio("chat_privacy_delete", "dato privado", "respuesta privada")
    main.guardar_memoria("dato para borrar", "general")
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        bad_phrase = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": "test-password-123", "confirmation": "borrar todo"
        })
        assert bad_phrase.status_code == 400
        bad_password = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": "incorrecta", "confirmation": "ELIMINAR MIS DATOS"
        })
        assert bad_password.status_code == 403
        deleted = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": "test-password-123", "confirmation": "ELIMINAR MIS DATOS"
        })
        assert deleted.status_code == 200
        assert deleted.json()["account_preserved"] is True
        assert client.get("/export", headers=headers).status_code == 401
        new_token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        exported = client.get("/export", headers={"Authorization": f"Bearer {new_token}"}).json()
        assert not any(row["conversation_id"] == "chat_privacy_delete" for row in exported["conversations"])
        assert not any(row["content"] == "dato para borrar" for row in exported["memories"])
