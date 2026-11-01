import asyncio
import httpx
import pytest
from fastapi.testclient import TestClient
import main
from busqueda_web import buscar_web, SEARCH_ENDPOINT

HTML = '''<html><body>
<div class="result"><a class="result__a" href="https://example.com/a">Ejemplo uno</a><a class="result__snippet">Fragmento útil de la fuente.</a></div>
<div class="result"><a class="result__a" href="javascript:alert(1)">URL mala</a></div>
<div class="result"><a class="result__a" href="https://example.org/b">Ejemplo dos</a><a class="result__snippet">Otro fragmento.</a></div>
</body></html>'''


def test_search_parses_results_and_rejects_non_http_urls():
    async def handler(request):
        assert str(request.url) == SEARCH_ENDPOINT
        assert request.method == "POST"
        return httpx.Response(200, text=HTML)
    transport = httpx.MockTransport(handler)
    results = asyncio.run(buscar_web("  prueba   de búsqueda ", limit=5, transport=transport))
    assert len(results) == 2
    assert results[0]["title"] == "Ejemplo uno"
    assert results[0]["url"] == "https://example.com/a"
    assert "Fragmento útil" in results[0]["snippet"]


def test_search_rejects_empty_and_long_queries():
    with pytest.raises(ValueError, match="consulta"):
        asyncio.run(buscar_web("  "))
    with pytest.raises(ValueError, match="300 caracteres"):
        asyncio.run(buscar_web("x" * 301))


def test_web_search_endpoint_requires_authentication():
    with TestClient(main.app) as client:
        response = client.post("/tools/web-search", json={"query": "prueba"})
    assert response.status_code in (401, 403)


def test_web_search_endpoint_returns_sources(monkeypatch):
    async def fake_search(query, limit=5):
        assert query == "fuente confiable"
        return [{"title": "Fuente", "url": "https://example.com", "snippet": "Fragmento"}]
    monkeypatch.setattr(main, "buscar_web", fake_search)
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    try:
        with TestClient(main.app) as client:
            response = client.post("/tools/web-search", json={"query": "fuente confiable", "limit": 1})
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["count"] == 1
        assert payload["results"][0]["url"] == "https://example.com"
    finally:
        main.app.dependency_overrides.clear()


def test_search_unwraps_redirects_and_removes_tracking_parameters():
    from urllib.parse import quote
    redirect = "https://html.duckduckgo.com/l/?uddg=" + quote("https://Example.com/story?utm_source=ddg&id=7#section", safe="")
    html_doc = f'<a class="result__a" href="{redirect}">Historia</a>'
    async def handler(request):
        return httpx.Response(200, text=html_doc)
    results = asyncio.run(buscar_web("historia", transport=httpx.MockTransport(handler)))
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/story?id=7"
    assert results[0]["domain"] == "example.com"


def test_search_rejects_local_and_non_public_targets():
    from busqueda_web import _normalize_result_url
    assert _normalize_result_url("http://127.0.0.1/admin") is None
    assert _normalize_result_url("http://localhost/login") is None
    assert _normalize_result_url("file:///etc/passwd") is None
    assert _normalize_result_url("https://user:pass@example.com/path") is None


def test_web_search_endpoint_includes_domain_metadata(monkeypatch):
    async def fake_search(query, limit=5):
        return [{"title": "Fuente", "url": "https://example.com/a", "domain": "example.com", "snippet": "Fragmento"}]
    monkeypatch.setattr(main, "buscar_web", fake_search)
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    try:
        with TestClient(main.app) as client:
            response = client.post("/tools/web-search", json={"query": "fuente confiable", "limit": 1})
        assert response.status_code == 200
        assert response.json()["results"][0]["domain"] == "example.com"
    finally:
        main.app.dependency_overrides.clear()
