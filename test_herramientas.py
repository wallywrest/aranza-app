import pytest
import asyncio
from fastapi.testclient import TestClient
import main
from herramientas import ToolInputError, validate_tool_request, list_tool_contracts


def test_catalog_contracts_are_explicit_and_safe():
    items = list_tool_contracts()
    names = {item["name"] for item in items}
    assert {"web_search", "web_research", "read_webpage", "file_analysis", "vision"} <= names
    assert all("api_key" not in str(item).lower() for item in items)
    assert next(x for x in items if x["name"] == "vision")["execution_mode"] == "dedicated_upload"


@pytest.mark.parametrize("payload", [
    None, [], {"name": "shell", "arguments": {}},
    {"name": "web_search", "arguments": {"query": "ok", "extra": "x"}},
    {"name": "web_search", "arguments": {"query": " "}},
    {"name": "web_search", "arguments": {"query": "x", "limit": True}},
    {"name": "read_webpage", "arguments": {"url": "x", "headers": {"Authorization": "secret"}}},
    {"name": "vision", "arguments": {"file": "fake.png"}},
])
def test_rejects_invalid_or_untrusted_tool_payloads(payload):
    with pytest.raises(ToolInputError):
        validate_tool_request(payload)


def test_normalizes_search_request():
    name, args = validate_tool_request({"name": "web_search", "arguments": {"query": "  energía   solar ", "limit": 3}})
    assert name == "web_search"
    assert args == {"query": "energía solar", "limit": 3}


def test_unified_executor_requires_authentication():
    with TestClient(main.app) as client:
        assert client.get("/tools/catalog").status_code in (401, 403)
        assert client.post("/tools/execute", json={"name": "web_search", "arguments": {"query": "test"}}).status_code in (401, 403)


def test_unified_executor_runs_search_with_trace(monkeypatch):
    async def fake_search(query, limit=5):
        assert query == "fuente segura"
        assert limit == 2
        return [{"title": "Fuente", "url": "https://example.com", "domain": "example.com", "snippet": "Texto"}]
    monkeypatch.setattr(main, "buscar_web", fake_search)
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    try:
        with TestClient(main.app) as client:
            response = client.post("/tools/execute", json={"name": "web_search", "arguments": {"query": "fuente segura", "limit": 2}})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["tool"] == "web_search"
        assert data["status"] == "completed"
        assert data["read_only"] is True
        assert data["duration_ms"] >= 0
        assert data["result"]["count"] == 1
    finally:
        main.app.dependency_overrides.clear()


def test_unified_executor_rejects_unknown_tool_without_execution(monkeypatch):
    called = False
    async def fake_search(*args, **kwargs):
        nonlocal called
        called = True
        return []
    monkeypatch.setattr(main, "buscar_web", fake_search)
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    try:
        with TestClient(main.app) as client:
            response = client.post("/tools/execute", json={"name": "run_shell", "arguments": {}})
        assert response.status_code == 422
        assert called is False
    finally:
        main.app.dependency_overrides.clear()


def _login_headers(client):
    main.inicializar_db()
    salt, digest = main.generar_hash_contrasena("test-password-123")
    with main.conectar_db() as conn:
        conn.execute(
            "UPDATE cuentas SET username='owner', password_salt=?, password_hash=?, password_iterations=? WHERE account_id='owner'",
            (salt, digest, main.PASSWORD_HASH_ITERATIONS),
        )
        conn.execute("DELETE FROM sesiones")
        conn.execute("DELETE FROM intentos_login")
    main._login_attempts.clear()
    login = client.post("/login", json={"username": "owner", "password": "test-password-123"})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_chat_executes_only_bounded_read_only_web_search(monkeypatch):
    calls = []
    async def fake_search(query, limit=5):
        calls.append((query, limit))
        return [{"title": "Fuente pública", "url": "https://example.com/a", "domain": "example.com", "snippet": "Dato de prueba"}]

    async def fake_completion(messages, **kwargs):
        system_context = "\n".join(m["content"] for m in messages if m["role"] == "system")
        assert "Fuente pública" in system_context
        assert "NO CONFIABLE" in system_context
        return "Respuesta con fuente.", {"provider": "test", "model": "fake"}

    monkeypatch.setattr(main, "buscar_web", fake_search)
    monkeypatch.setattr(main, "completar_chat", fake_completion)
    with TestClient(main.app) as client:
        headers = _login_headers(client)
        response = client.post("/chat", headers=headers, json={
            "message": "Investiga energía solar", "conversation_id": "auto-tool-test"
        })
    assert response.status_code == 200, response.text
    payload = response.json()
    assert calls == [("Investiga energía solar", 3)]
    assert payload["tool_trace"][0]["tool"] == "web_research"
    assert payload["tool_trace"][0]["status"] == "completed"
    assert payload["tool_trace"][0]["pages_read"] == 0
    planned = next(x for x in payload["execution_plan"]["tools"] if x["name"] == "web_research")
    assert planned["status"] == "completed"
    assert "solo lectura" in payload["execution_plan"]["execution_policy"]


def test_chat_does_not_execute_tools_for_normal_conversation(monkeypatch):
    calls = []
    async def fake_search(*args, **kwargs):
        calls.append(args)
        return []
    async def fake_completion(messages, **kwargs):
        return "Hola.", {"provider": "test", "model": "fake"}
    monkeypatch.setattr(main, "buscar_web", fake_search)
    monkeypatch.setattr(main, "completar_chat", fake_completion)
    with TestClient(main.app) as client:
        headers = _login_headers(client)
        response = client.post("/chat", headers=headers, json={
            "message": "Hola, ¿cómo estás?", "conversation_id": "no-tool-test"
        })
    assert response.status_code == 200, response.text
    assert calls == []
    assert response.json()["tool_trace"] == []


def test_chat_research_reads_at_most_two_pages(monkeypatch):
    calls = []
    async def fake_search(query, limit=5):
        return [
            {"title": f"Fuente {i}", "url": f"https://example.com/{i}", "domain": "example.com", "snippet": "fragmento"}
            for i in range(4)
        ]
    async def fake_read(url):
        calls.append(url)
        return {"url": url, "title": "Página", "text": "Contenido verificable"}
    async def fake_completion(messages, **kwargs):
        context = "\n".join(m["content"] for m in messages if m["role"] == "system")
        assert "Contenido verificable" in context
        assert "NO CONFIABLE" in context
        return "Síntesis limitada.", {"provider": "test", "model": "fake"}
    monkeypatch.setattr(main, "buscar_web", fake_search)
    monkeypatch.setattr(main, "leer_pagina", fake_read)
    monkeypatch.setattr(main, "completar_chat", fake_completion)
    with TestClient(main.app) as client:
        headers = _login_headers(client)
        response = client.post("/chat", headers=headers, json={
            "message": "Investiga fuentes sobre energía solar", "conversation_id": "research-tool-test"
        })
    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(calls) == 2
    assert payload["tool_trace"][0]["tool"] == "web_research"
    assert payload["tool_trace"][0]["pages_read"] == 2
    assert payload["tool_trace"][0]["result_count"] == 3


def test_chat_research_timeout_is_reported_without_fabricating_sources(monkeypatch):
    async def slow_search(query, limit=5):
        await asyncio.sleep(25)
        return []
    async def fake_completion(messages, **kwargs):
        assert any("superó su límite de" in m["content"] for m in messages if m["role"] == "system")
        return "No pude consultar fuentes en este turno.", {"provider": "test", "model": "fake"}
    monkeypatch.setattr(main, "CHAT_TOOL_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(main, "buscar_web", slow_search)
    monkeypatch.setattr(main, "completar_chat", fake_completion)
    with TestClient(main.app) as client:
        headers = _login_headers(client)
        response = client.post("/chat", headers=headers, json={
            "message": "Investiga el tema de prueba", "conversation_id": "research-timeout-test"
        })
    assert response.status_code == 200, response.text
    trace = response.json()["tool_trace"][0]
    assert trace["status"] == "timeout"
    assert trace["result_count"] == 0
