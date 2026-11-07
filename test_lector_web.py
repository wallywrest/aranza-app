import asyncio
import socket
from urllib.parse import urlparse

import aiohttp
import pytest
from aiohttp.abc import AbstractResolver

import lector_web
from lector_web import PublicResolver, _clean_url, leer_pagina

HTML = """<html><head><title>Artículo de prueba</title><script>secreto()</script></head>
<body><nav>Menú que se omite</nav><main><h1>Encabezado</h1><p>Texto importante de la página.</p><p>Segundo párrafo.</p></main></body></html>"""


class StubResolver(AbstractResolver):
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []
        self.closed = False

    async def resolve(self, host, port=0, family=socket.AF_UNSPEC):
        self.calls.append((host, port, family))
        if not self.answers:
            return []
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return [{
            "hostname": host,
            "host": address,
            "port": port,
            "family": socket.AF_INET6 if ":" in address else socket.AF_INET,
            "proto": socket.IPPROTO_TCP,
            "flags": 0,
        } for address in answer]

    async def close(self):
        self.closed = True


class FakeContent:
    def __init__(self, content):
        self.content = content

    async def iter_chunked(self, chunk_size):
        for index in range(0, len(self.content), chunk_size):
            yield self.content[index:index + chunk_size]


class FakeResponse:
    def __init__(self, status=200, headers=None, content=HTML.encode()):
        self.status = status
        self.headers = headers or {"content-type": "text/html; charset=utf-8"}
        self.content = FakeContent(content)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    def raise_for_status(self):
        if self.status >= 400:
            raise RuntimeError("HTTP error")


class FakeSession:
    def __init__(self, response, connector):
        self.response = response
        self.connector = connector
        self.requests = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.connector.close()

    def get(self, url, **kwargs):
        self.requests.append((url, kwargs))
        return self.response


def _install_fake_session(monkeypatch, response):
    captured = {}

    def build_session(**kwargs):
        session = FakeSession(response, kwargs["connector"])
        captured["session"] = session
        captured["connector"] = kwargs["connector"]
        return session

    monkeypatch.setattr(lector_web.aiohttp, "ClientSession", build_session)
    return captured


def _record(address):
    return [address]


def test_url_policy_rejects_unsafe_schemes_hosts_credentials_and_ports():
    unsafe = (
        "file:///etc/passwd",
        "http://127.0.0.1/admin",
        "http://192.168.1.1/",
        "https://user:pass@example.com",
        "http://localhost/",
        "http://printer.local/",
        "http://example.com:8080/",
        "https://example.com:8443/",
        "http://example.com:invalid/",
    )
    for url in unsafe:
        with pytest.raises(ValueError):
            _clean_url(url)
    assert _clean_url("https://Example.com/a#fragment") == "https://example.com/a"


@pytest.mark.parametrize("address", [
    "127.0.0.1", "10.1.2.3", "169.254.169.254", "192.168.0.1",
    "::1", "fe80::1", "fc00::1", "224.0.0.1", "::ffff:127.0.0.1",
])
def test_public_resolver_rejects_private_local_reserved_and_mapped_addresses(address):
    raw = StubResolver([_record(address)])
    resolver = PublicResolver(raw)
    with pytest.raises(ValueError, match="no pública"):
        asyncio.run(resolver.resolve("example.com", 443, socket.AF_UNSPEC))


def test_public_resolver_returns_validated_addresses_for_the_connector():
    raw = StubResolver([_record("93.184.216.34"), _record("2606:4700:4700::1111")])
    resolver = PublicResolver(raw)
    first = asyncio.run(resolver.resolve("example.com", 443, socket.AF_UNSPEC))
    second = asyncio.run(resolver.resolve("example.com", 443, socket.AF_UNSPEC))
    assert [item["host"] for item in first] == ["93.184.216.34"]
    assert [item["host"] for item in second] == ["2606:4700:4700::1111"]


def test_dns_rebinding_is_revalidated_on_each_connection_resolution():
    raw = StubResolver([_record("93.184.216.34"), _record("127.0.0.1")])
    resolver = PublicResolver(raw)
    first = asyncio.run(resolver.resolve("example.com", 443, socket.AF_UNSPEC))
    assert first[0]["host"] == "93.184.216.34"
    with pytest.raises(ValueError, match="no pública"):
        asyncio.run(resolver.resolve("example.com", 443, socket.AF_UNSPEC))
    assert len(raw.calls) == 2


@pytest.mark.parametrize("host", ["127.1", "0177.0.0.1", "0x7f000001", "2130706433"])
def test_alternate_ipv4_spellings_cannot_resolve_to_loopback(host):
    try:
        clean = _clean_url(f"http://{host}/")
    except ValueError:
        return
    parsed_host = urlparse(clean).hostname
    resolver = PublicResolver(StubResolver([_record("127.0.0.1")]))
    with pytest.raises(ValueError, match="no pública"):
        asyncio.run(resolver.resolve(parsed_host, 80, socket.AF_UNSPEC))


def test_reader_attaches_public_resolver_to_connector_and_extracts_html(monkeypatch):
    response = FakeResponse()
    captured = _install_fake_session(monkeypatch, response)
    resolver = PublicResolver(StubResolver([_record("93.184.216.34")]))
    result = asyncio.run(leer_pagina("https://example.com/article", _resolver=resolver))
    assert captured["connector"]._resolver is resolver
    assert captured["session"].requests[0][1]["allow_redirects"] is False
    assert result["title"] == "Artículo de prueba"
    assert "Texto importante" in result["text"]
    assert "secreto()" not in result["text"]
    assert "Menú que se omite" not in result["text"]


def test_reader_rejects_redirect_to_internal_without_following_it(monkeypatch):
    response = FakeResponse(
        status=302,
        headers={"location": "http://127.0.0.1/admin", "content-type": "text/html"},
    )
    captured = _install_fake_session(monkeypatch, response)
    resolver = PublicResolver(StubResolver([_record("93.184.216.34")]))
    with pytest.raises(ValueError, match="redirige"):
        asyncio.run(leer_pagina("https://example.com/article", _resolver=resolver))
    assert len(captured["session"].requests) == 1
    assert captured["session"].requests[0][1]["allow_redirects"] is False


def test_reader_rejects_compressed_and_non_html_responses(monkeypatch):
    compressed = FakeResponse(headers={
        "content-type": "text/html",
        "content-encoding": "gzip",
    })
    _install_fake_session(monkeypatch, compressed)
    with pytest.raises(ValueError, match="compresión"):
        asyncio.run(leer_pagina(
            "https://example.com/file",
            _resolver=PublicResolver(StubResolver([_record("93.184.216.34")])),
        ))

    non_html = FakeResponse(headers={"content-type": "application/pdf"}, content=b"pdf")
    _install_fake_session(monkeypatch, non_html)
    with pytest.raises(ValueError, match="HTML"):
        asyncio.run(leer_pagina(
            "https://example.com/file",
            _resolver=PublicResolver(StubResolver([_record("93.184.216.34")])),
        ))
