from fastapi.testclient import TestClient
import main


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DATABASE_PATH', str(tmp_path / 'library-v195.sqlite3'))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {'account_id': 'owner'}
    client = TestClient(main.app)
    saved = client.post('/research/library', json={
        'title': 'Energía solar en México', 'query': 'capacidad instalada',
        'summary': 'La capacidad creció según las fuentes consultadas.',
        'sources': [{'title': 'Informe energético', 'url': 'https://example.org/informe', 'domain': 'example.org', 'snippet': 'Capacidad instalada reportada.', 'page_read': True}],
        'evidence': {'status': 'partial', 'claims': 2}
    })
    assert saved.status_code == 200
    return client, saved.json()['research_id']


def test_research_library_search_filters_title_query_and_summary(tmp_path, monkeypatch):
    client, rid = _setup(tmp_path, monkeypatch)
    try:
        result = client.get('/research/library', params={'q': 'solar'}).json()['investigations']
        assert [item['id'] for item in result] == [rid]
        assert client.get('/research/library', params={'q': 'nada'}).json()['investigations'] == []
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_research_export_markdown_is_authenticated_and_account_scoped(tmp_path, monkeypatch):
    client, rid = _setup(tmp_path, monkeypatch)
    try:
        response = client.get(f'/research/library/{rid}/export')
        assert response.status_code == 200
        assert 'text/markdown' in response.headers['content-type']
        assert '# Energía solar en México' in response.text
        assert 'https://example.org/informe' in response.text
        assert '"status": "partial"' in response.text
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_research_library_frontend_has_search_detail_and_export_controls():
    from pathlib import Path
    html = Path(main.BASE_DIR / 'index.html').read_text(encoding='utf-8')
    assert 'Biblioteca de investigaciones' in html
    assert 'research-library-query' in html
    assert 'Exportar Markdown' in html
    assert 'research-delete-btn' in html
