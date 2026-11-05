import json
from pathlib import Path

BASE = Path(__file__).parent

def test_manifest_is_valid_and_installable():
    manifest = json.loads((BASE / 'manifest.webmanifest').read_text(encoding="utf-8"))
    assert manifest['name'] == 'Aranza AI'
    assert manifest['start_url'] == '/'
    assert manifest['display'] == 'standalone'
    assert (BASE / 'icons' / 'aranza.svg').is_file()

def test_service_worker_caches_only_public_shell():
    worker = (BASE / 'sw.js').read_text(encoding="utf-8")
    assert "const SHELL = ['/', '/manifest.webmanifest', '/icons/aranza.svg']" in worker
    assert "request.method !== 'GET'" in worker
    assert "url.pathname.startsWith('/api')" in worker
    assert 'Authorization' not in worker

def test_frontend_registers_service_worker_and_manifest():
    html = (BASE / 'index.html').read_text(encoding="utf-8")
    assert 'rel="manifest"' in html
    assert "navigator.serviceWorker.register('/sw.js')" in html
