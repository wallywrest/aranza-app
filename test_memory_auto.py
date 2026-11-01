"""Pruebas de memoria explícita y revisión del ámbito de cuenta."""
import main
from fastapi.testclient import TestClient


def setup_function():
    main.inicializar_db()
    salt, digest = main.generar_hash_contrasena("test-password-123")
    with main.conectar_db() as conn:
        conn.execute("UPDATE cuentas SET username='owner', password_salt=?, password_hash=?, password_iterations=? WHERE account_id='owner'",
                     (salt, digest, main.PASSWORD_HASH_ITERATIONS))
        conn.execute("DELETE FROM memorias")
        conn.execute("DELETE FROM sesiones")
        conn.execute("DELETE FROM intentos_login")
    main._login_attempts.clear()


def test_extracts_only_explicit_memory_requests():
    result = main.extraer_recuerdo_explicito("Recuerda que prefiero respuestas directas")
    assert result == {"content": "prefiero respuestas directas", "category": "preferencias"}
    assert main.extraer_recuerdo_explicito("Prefiero respuestas directas") is None
    assert main.extraer_recuerdo_explicito("No recuerdes que prefiero respuestas directas") is None


def test_rejects_credentials_and_oversized_memory():
    assert main.extraer_recuerdo_explicito("Recuerda que mi contraseña es abc123") is None
    assert main.extraer_recuerdo_explicito("Recuerda que " + "x" * 1100) is None


def test_memory_deduplicates_within_account_and_keeps_scope():
    item = {"content": "Prefiero respuestas directas", "category": "preferencias"}
    first_id = main.guardar_recuerdo_si_nuevo(item, account_id="owner")
    second_id = main.guardar_recuerdo_si_nuevo(item, account_id="owner")
    other_account_id = main.guardar_recuerdo_si_nuevo(item, account_id="another-account")
    assert first_id is not None
    assert second_id is None
    assert other_account_id is not None
    assert len(main.obtener_memorias(account_id="owner")) == 1
    assert len(main.obtener_memorias(account_id="another-account")) == 1


def test_chat_saves_explicit_memory_and_returns_confirmation(monkeypatch):
    async def fake_completar_chat(*args, **kwargs):
        return "Entendido.", {"provider": "test", "model": "fake-model"}
    monkeypatch.setattr(main, "completar_chat", fake_completar_chat)

    with TestClient(main.app) as client:
        login = client.post("/login", json={"username": "owner", "password": "test-password-123"})
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        response = client.post("/chat", headers=headers, json={
            "message": "Recuerda que mi objetivo es aprender Excel", "conversation_id": "memory-test"
        })
        assert response.status_code == 200
        payload = response.json()
        assert payload["memory_saved"] is True
        assert "Guardé ese dato" in payload["response"]
        memories = client.get("/memory", headers=headers).json()["memories"]
        assert len(memories) == 1
        assert memories[0]["content"] == "mi objetivo es aprender Excel"


def test_chat_does_not_confirm_duplicate_as_new_memory(monkeypatch):
    async def fake_completar_chat(*args, **kwargs):
        return "Entendido.", {"provider": "test", "model": "fake-model"}
    monkeypatch.setattr(main, "completar_chat", fake_completar_chat)
    with TestClient(main.app) as client:
        login = client.post("/login", json={"username": "owner", "password": "test-password-123"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        body = {"message": "Recuerda que prefiero respuestas directas", "conversation_id": "memory-dupe"}
        assert client.post("/chat", headers=headers, json=body).json()["memory_saved"] is True
        repeated = client.post("/chat", headers=headers, json=body).json()
        assert repeated["memory_saved"] is False
        assert "Guardé ese dato" not in repeated["response"]
        assert len(client.get("/memory", headers=headers).json()["memories"]) == 1
