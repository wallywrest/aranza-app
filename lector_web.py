"""Lector limitado de páginas web públicas para Aranza.

No sigue redirecciones, solo admite HTTP(S), rechaza hosts/IP no públicos,
limita bytes y extrae texto sin ejecutar scripts. No es un navegador completo.
"""
from __future__ import annotations
import asyncio
import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse
import httpx

MAX_URL_LENGTH = 2000
MAX_HTML_BYTES = 1_000_000
MAX_TEXT_CHARS = 12_000
TIMEOUT_SECONDS = 10
BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".test", ".example", ".invalid")

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
        if tag == "title": self.in_title = True
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "iframe", "nav", "footer", "header") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title": self.in_title = False
        if tag in ("p", "div", "main", "article", "section", "h1", "h2", "h3", "li", "br"):
            self.parts.append("\n")
    def handle_data(self, data):
        if self.in_title: self.title_parts.append(data)
        if not self.skip_depth: self.parts.append(data)

def _clean_url(url: str) -> str:
    if not isinstance(url, str) or len(url) > MAX_URL_LENGTH:
        raise ValueError("La URL no es válida o supera el límite permitido.")
    p = urlparse(url.strip())
    if p.scheme.lower() not in ("http", "https") or not p.hostname:
        raise ValueError("Solo se admiten URLs HTTP o HTTPS.")
    if p.username or p.password:
        raise ValueError("No se admiten credenciales dentro de la URL.")
    host = p.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(BLOCKED_SUFFIXES):
        raise ValueError("No se permiten destinos locales o reservados.")
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise ValueError("No se permiten direcciones IP privadas o reservadas.")
    except ValueError as exc:
        if "No se permiten" in str(exc): raise
        if "." not in host or any(not x or len(x) > 63 for x in host.split(".")):
            raise ValueError("El dominio no es válido.") from exc
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path or "/", "", p.query, ""))

async def _validate_public_dns(host: str):
    try:
        infos = await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo(host, None, type=socket.SOCK_STREAM), timeout=3)
    except Exception as exc:
        raise ValueError("No se pudo validar el dominio público.") from exc
    addresses = {info[4][0] for info in infos}
    if not addresses:
        raise ValueError("El dominio no tiene direcciones válidas.")
    for address in addresses:
        try: ip = ipaddress.ip_address(address)
        except ValueError as exc: raise ValueError("Respuesta DNS no válida.") from exc
        if not ip.is_global:
            raise ValueError("El dominio resuelve a una dirección no pública.")

async def leer_pagina(url: str, *, transport=None) -> dict[str, str | int]:
    clean = _clean_url(url)
    host = urlparse(clean).hostname or ""
    await _validate_public_dns(host)
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=False, trust_env=False,
                                 transport=transport, headers={"User-Agent":"AranzaReader/1.19"}) as client:
        async with client.stream("GET", clean, headers={"Accept":"text/html,application/xhtml+xml"}) as response:
            if response.status_code in (301,302,303,307,308):
                raise ValueError("La página redirige. Usa el enlace final de la fuente y vuelve a intentarlo.")
            response.raise_for_status()
            ctype = response.headers.get("content-type", "").lower()
            if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
                raise ValueError("La URL no devuelve una página HTML.")
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                if len(data) > MAX_HTML_BYTES:
                    raise ValueError("La página supera el límite de 1 MB.")
    encoding = "utf-8"
    match = re.search(br"charset\s*=\s*['\"]?([\w-]+)", bytes(data[:4096]), re.I)
    if match:
        try: encoding = match.group(1).decode("ascii")
        except Exception: pass
    try: source = data.decode(encoding, errors="replace")
    except LookupError: source = data.decode("utf-8", errors="replace")
    parser = _TextExtractor()
    parser.feed(source)
    text = re.sub(r"[ \t]+", " ", "".join(parser.parts))
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    if not text:
        raise ValueError("No se encontró texto legible en la página.")
    return {"url": clean, "title": re.sub(r"\s+", " ", "".join(parser.title_parts)).strip()[:300],
            "text": text[:MAX_TEXT_CHARS], "characters": min(len(text), MAX_TEXT_CHARS),
            "truncated": len(text) > MAX_TEXT_CHARS, "stored": False}
