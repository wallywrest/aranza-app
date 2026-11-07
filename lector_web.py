"""Lector limitado de páginas públicas con conexión ligada a DNS validado.

No sigue redirecciones, solo admite HTTP(S) en puertos estándar, rechaza
destinos no públicos y limita bytes/texto. No ejecuta JavaScript.
"""
from __future__ import annotations

import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse

import aiohttp
from aiohttp.abc import AbstractResolver
from aiohttp.resolver import DefaultResolver

MAX_URL_LENGTH = 2000
MAX_HTML_BYTES = 1_000_000
MAX_TEXT_CHARS = 12_000
TIMEOUT_SECONDS = 10
DNS_TIMEOUT_SECONDS = 3
BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".test", ".example", ".invalid")
_ALLOWED_PORTS = {"http": 80, "https": 443}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0
        self.title_parts = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg", "iframe", "nav", "footer", "header"):
            self.skip_depth += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "iframe", "nav", "footer", "header") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title":
            self.in_title = False
        if tag in ("p", "div", "main", "article", "section", "h1", "h2", "h3", "li", "br"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if not self.skip_depth:
            self.parts.append(data)


def _parse_ip_address(value: str):
    if "%" in value:
        raise ValueError("No se permiten identificadores de zona en una IP.")
    address = ipaddress.ip_address(value)
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        return address.ipv4_mapped
    return address


def _is_public_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        address.is_global
        and not address.is_private
        and not address.is_loopback
        and not address.is_link_local
        and not address.is_multicast
        and not address.is_reserved
        and not address.is_unspecified
    )


def _clean_url(url: str) -> str:
    if not isinstance(url, str) or len(url) > MAX_URL_LENGTH:
        raise ValueError("La URL no es válida o supera el límite permitido.")
    if any(ord(char) < 32 or ord(char) == 127 for char in url):
        raise ValueError("La URL contiene caracteres de control.")

    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    if scheme not in _ALLOWED_PORTS or not parsed.hostname:
        raise ValueError("Solo se admiten URLs HTTP o HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("No se admiten credenciales dentro de la URL.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("El puerto de la URL no es válido.") from exc
    if port is not None and port != _ALLOWED_PORTS[scheme]:
        raise ValueError("Solo se permiten los puertos HTTP y HTTPS estándar.")

    raw_host = parsed.hostname.rstrip(".").lower()
    if not raw_host or "%" in raw_host:
        raise ValueError("El nombre de host no es válido.")

    try:
        address = _parse_ip_address(raw_host)
    except ValueError:
        address = None

    if address is not None:
        if not _is_public_address(address):
            raise ValueError("No se permiten direcciones IP privadas o reservadas.")
        host = address.compressed
    else:
        if raw_host == "localhost" or raw_host.endswith(BLOCKED_SUFFIXES):
            raise ValueError("No se permiten destinos locales o reservados.")
        try:
            host = raw_host.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("El dominio no es válido.") from exc
        labels = host.split(".")
        if (
            len(host) > 253
            or len(labels) < 2
            or any(
                not label
                or len(label) > 63
                or label.startswith("-")
                or label.endswith("-")
                or not re.fullmatch(r"[a-z0-9-]+", label)
                for label in labels
            )
        ):
            raise ValueError("El dominio no es válido.")

    authority_host = f"[{host}]" if ":" in host else host
    authority = authority_host + (f":{port}" if port is not None else "")
    return urlunparse((scheme, authority, parsed.path or "/", parsed.params, parsed.query, ""))


class PublicResolver(AbstractResolver):
    """Entrega al conector solo IP públicas y valida cada resolución usada."""

    def __init__(self, resolver: AbstractResolver | None = None):
        self._resolver = resolver or DefaultResolver()

    async def resolve(self, host, port=0, family=socket.AF_UNSPEC):
        normalized_host = str(host).rstrip(".").lower()
        try:
            literal = _parse_ip_address(normalized_host)
        except ValueError:
            literal = None

        if literal is not None:
            addresses = [{
                "hostname": normalized_host,
                "host": literal.compressed,
                "port": port,
                "family": socket.AF_INET6 if literal.version == 6 else socket.AF_INET,
                "proto": socket.IPPROTO_TCP,
                "flags": 0,
            }]
        else:
            try:
                addresses = await self._resolver.resolve(normalized_host, port, family)
            except Exception as exc:
                raise OSError("No se pudo resolver el dominio público.") from exc

        if not addresses:
            raise OSError("El dominio no tiene direcciones válidas.")

        validated = []
        seen = set()
        for result in addresses:
            try:
                address = _parse_ip_address(str(result["host"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("La respuesta DNS no es válida.") from exc
            if not _is_public_address(address):
                raise ValueError("El dominio resuelve a una dirección no pública.")
            key = (address.version, address.compressed)
            if key in seen:
                continue
            seen.add(key)
            validated.append({
                "hostname": normalized_host,
                "host": address.compressed,
                "port": port,
                "family": socket.AF_INET6 if address.version == 6 else socket.AF_INET,
                "proto": socket.IPPROTO_TCP,
                "flags": 0,
            })
        return validated

    async def close(self):
        await self._resolver.close()


async def leer_pagina(url: str, *, _resolver: AbstractResolver | None = None) -> dict[str, str | int]:
    clean = _clean_url(url)
    connector = aiohttp.TCPConnector(
        resolver=_resolver or PublicResolver(),
        use_dns_cache=False,
        force_close=True,
        limit=1,
        ssl=True,
    )
    timeout = aiohttp.ClientTimeout(
        total=TIMEOUT_SECONDS,
        connect=DNS_TIMEOUT_SECONDS,
        sock_read=TIMEOUT_SECONDS,
    )
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        trust_env=False,
        auto_decompress=False,
        headers={"User-Agent": "AranzaReader/1.20"},
    ) as client:
        async with client.get(
            clean,
            allow_redirects=False,
            headers={"Accept": "text/html,application/xhtml+xml", "Accept-Encoding": "identity"},
        ) as response:
            if 300 <= response.status < 400:
                raise ValueError("La página redirige. Usa el enlace final de la fuente y vuelve a intentarlo.")
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                raise ValueError("La URL no devuelve una página HTML.")
            content_encoding = response.headers.get("content-encoding", "identity").lower()
            if content_encoding not in ("", "identity"):
                raise ValueError("La página usa una compresión no admitida.")
            data = bytearray()
            async for chunk in response.content.iter_chunked(65536):
                if len(data) + len(chunk) > MAX_HTML_BYTES:
                    raise ValueError("La página supera el límite de 1 MB.")
                data.extend(chunk)

    encoding = "utf-8"
    match = re.search(br"charset\s*=\s*['\"]?([\w-]+)", bytes(data[:4096]), re.I)
    if match:
        try:
            encoding = match.group(1).decode("ascii")
        except Exception:
            pass
    try:
        source = data.decode(encoding, errors="replace")
    except LookupError:
        source = data.decode("utf-8", errors="replace")
    parser = _TextExtractor()
    parser.feed(source)
    text = re.sub(r"[ \t]+", " ", "".join(parser.parts))
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    if not text:
        raise ValueError("No se encontró texto legible en la página.")
    return {
        "url": clean,
        "title": re.sub(r"\s+", " ", "".join(parser.title_parts)).strip()[:300],
        "text": text[:MAX_TEXT_CHARS],
        "characters": min(len(text), MAX_TEXT_CHARS),
        "truncated": len(text) > MAX_TEXT_CHARS,
        "stored": False,
    }
