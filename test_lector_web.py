import asyncio
import httpx
import pytest
import lector_web
from lector_web import leer_pagina, _clean_url

HTML = '''<html><head><title>Artículo de prueba</title><script>secreto()</script></head>
<body><nav>Menú que se omite</nav><main><h1>Encabezado</h1><p>Texto importante de la página.</p><p>Segundo párrafo.</p></main></body></html>'''

def test_url_policy_rejects_private_and_unsafe_urls():
    for url in ("file:///etc/passwd", "http://127.0.0.1/admin", "http://192.168.1.1/", "https://user:pass@example.com", "http://localhost/"):
        with pytest.raises(ValueError): _clean_url(url)
    assert _clean_url("https://Example.com/a#fragment") == "https://example.com/a"

def test_reader_extracts_text_and_never_follows_redirects(monkeypatch):
    async def public_dns(host):
        assert host == "example.com"
    monkeypatch.setattr(lector_web, "_validate_public_dns", public_dns)
    async def handler(request):
        return httpx.Response(200, headers={"content-type":"text/html; charset=utf-8"}, text=HTML)
    result = asyncio.run(leer_pagina("https://example.com/article", transport=httpx.MockTransport(handler)))
    assert result["title"] == "Artículo de prueba"
    assert "Texto importante" in result["text"]
    assert "secreto()" not in result["text"]
    assert "Menú que se omite" not in result["text"]
    async def redirect(request):
        return httpx.Response(302, headers={"location":"http://127.0.0.1/"})
    with pytest.raises(ValueError, match="redirige"):
        asyncio.run(leer_pagina("https://example.com/article", transport=httpx.MockTransport(redirect)))

def test_reader_rejects_non_html(monkeypatch):
    async def public_dns(host): return None
    monkeypatch.setattr(lector_web, "_validate_public_dns", public_dns)
    async def handler(request):
        return httpx.Response(200, headers={"content-type":"application/pdf"}, content=b"pdf")
    with pytest.raises(ValueError, match="HTML"):
        asyncio.run(leer_pagina("https://example.com/file", transport=httpx.MockTransport(handler)))

def test_read_webpage_endpoint_requires_authentication():
    from fastapi.testclient import TestClient
    import main
    with TestClient(main.app) as client:
        response = client.post("/tools/read-webpage", json={"url":"https://example.com"})
    assert response.status_code in (401,403)
