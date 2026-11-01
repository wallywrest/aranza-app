"""Búsqueda web controlada para Aranza.

Solo consulta un endpoint de búsqueda fijo. No descarga URLs arbitrarias, por lo
que esta herramienta no funciona como proxy abierto ni acepta destinos del usuario.
"""
from __future__ import annotations
import html
import re
from html.parser import HTMLParser
from urllib.parse import parse_qs, parse_qsl, urlencode, urljoin, urlparse, urlunparse
import ipaddress
import httpx

SEARCH_ENDPOINT = "https://html.duckduckgo.com/html/"
MAX_QUERY_LENGTH = 300

class _ResultsParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.results = []
        self._active = None
        self._capture = None
        self._snippet_depth = 0
        self._last_result = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get("class") or "").split())
        if tag == "a" and "result__a" in classes:
            self._active = {"title": "", "url": html.unescape(attrs.get("href", "")), "snippet": ""}
            self._capture = "title"
        elif "result__snippet" in classes and self._last_result is not None:
            self._capture = "snippet"
            self._snippet_depth = 1
        elif self._capture == "snippet" and tag in ("div", "span", "a"):
            self._snippet_depth += 1

    def handle_data(self, data):
        if self._active is not None and self._capture == "title":
            self._active["title"] += data
        elif self._capture == "snippet" and self._last_result is not None:
            self.results[self._last_result]["snippet"] += data

    def handle_endtag(self, tag):
        if self._active is not None and self._capture == "title" and tag == "a":
            if self._active["title"].strip():
                self.results.append(self._active)
                self._last_result = len(self.results) - 1
            self._active = None
            self._capture = None
        elif self._capture == "snippet" and tag in ("div", "span", "a"):
            self._snippet_depth -= 1
            if self._snippet_depth <= 0:
                self._capture = None

_TRACKING_PARAMS = {"fbclid", "gclid", "dclid", "mc_cid", "mc_eid", "ref", "ref_src"}


def _normalize_result_url(url: str) -> str | None:
    """Desenvuelve enlaces de DuckDuckGo y normaliza URLs públicas seguras."""
    try:
        url = urljoin(SEARCH_ENDPOINT, html.unescape((url or "").strip()))
        parsed = urlparse(url)
        if parsed.scheme == "https" and parsed.hostname in {"duckduckgo.com", "html.duckduckgo.com"}:
            target = parse_qs(parsed.query).get("uddg", [None])[0]
            if target:
                url = target
                parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return None
        if parsed.username or parsed.password:
            return None
        host = parsed.hostname.rstrip(".").lower()
        if host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".test")):
            return None
        try:
            ip = ipaddress.ip_address(host)
            if not ip.is_global:
                return None
        except ValueError:
            # Domain name: reject malformed host labels and obvious local names.
            if "." not in host or any(not label or len(label) > 63 for label in host.split(".")):
                return None
        filtered = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
                    if k.lower() not in _TRACKING_PARAMS and not k.lower().startswith("utm_")]
        path = parsed.path or "/"
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", urlencode(filtered, doseq=True), ""))
    except Exception:
        return None


def _valid_result_url(url: str) -> bool:
    return _normalize_result_url(url) is not None

async def buscar_web(query: str, *, limit: int = 5, transport=None) -> list[dict[str, str]]:
    query = re.sub(r"\s+", " ", (query or "")).strip()
    if not query:
        raise ValueError("Escribe una consulta para buscar en la web.")
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"La consulta no puede superar {MAX_QUERY_LENGTH} caracteres.")
    limit = max(1, min(int(limit), 8))
    async with httpx.AsyncClient(timeout=12.0, follow_redirects=False, transport=transport,
                                 headers={"User-Agent": "AranzaPersonalAI/1.16 (web search)"}) as client:
        response = await client.post(SEARCH_ENDPOINT, data={"q": query})
        response.raise_for_status()
    parser = _ResultsParser()
    parser.feed(response.text)
    clean = []
    seen = set()
    for item in parser.results:
        url = _normalize_result_url(item["url"])
        if not url or url in seen:
            continue
        seen.add(url)
        host = urlparse(url).hostname or ""
        clean.append({
            "title": re.sub(r"\s+", " ", item["title"]).strip()[:300],
            "url": url[:2000],
            "domain": host,
            "snippet": re.sub(r"\s+", " ", item["snippet"]).strip()[:700],
        })
        if len(clean) >= limit:
            break
    return clean
