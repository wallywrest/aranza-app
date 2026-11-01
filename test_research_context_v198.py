from fastapi.testclient import TestClient
import main


def test_chat_uses_relevant_private_research_context(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "DATABASE_PATH", str(tmp_path / "context.sqlite3"))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    async def fake_completion(messages, **kwargs):
        system_text = "\n".join(item["content"] for item in messages if item["role"] == "system")
        assert "CONTEXTO DE INVESTIGACIONES PREVIAS" in system_text
        assert "Energía solar fotovoltaica" in system_text
        assert "potencialmente desactualizado" in system_text
        return "Retomando la investigación previa.", {"provider": "test", "model": "fake"}

    monkeypatch.setattr(main, "completar_chat", fake_completion)
    with TestClient(main.app) as client:
        headers = {}
        saved = client.post("/research/library", headers=headers, json={
            "title": "Energía solar fotovoltaica",
            "query": "paneles solares y generación eléctrica",
            "summary": "Estudio de capacidad instalada y almacenamiento.",
            "sources": [{"title": "Informe renovable", "url": "https://example.org/solar", "page_read": True}],
            "evidence": {},
        })
        assert saved.status_code == 200, saved.text
        response = client.post("/chat", headers=headers, json={
            "message": "Explícame la energía solar fotovoltaica", "conversation_id": "research-context"
        })
    assert response.status_code == 200, response.text
    trace = response.json()["research_context"]
    assert trace["status"] == "used"
    assert trace["count"] == 1
    assert trace["method"] == "weighted_lexical_local"
    main.app.dependency_overrides.clear()


def test_chat_skips_unrelated_research_context(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "DATABASE_PATH", str(tmp_path / "context2.sqlite3"))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    async def fake_completion(messages, **kwargs):
        assert not any("CONTEXTO DE INVESTIGACIONES PREVIAS" in item["content"] for item in messages if item["role"] == "system")
        return "Hola.", {"provider": "test", "model": "fake"}
    monkeypatch.setattr(main, "completar_chat", fake_completion)
    with TestClient(main.app) as client:
        headers = {}
        client.post("/research/library", headers=headers, json={
            "title": "Historia del ferrocarril",
            "query": "locomotoras y transporte ferroviario",
            "summary": "Historia de los trenes.", "sources": [], "evidence": {}
        })
        response = client.post("/chat", headers=headers, json={"message": "Hola, ¿qué tal?", "conversation_id": "unrelated"})
    assert response.status_code == 200, response.text
    assert response.json()["research_context"]["status"] == "not_used"
    main.app.dependency_overrides.clear()
