from fastapi.testclient import TestClient
import main


def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DATABASE_PATH', str(tmp_path / 'library-v197.sqlite3'))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {'account_id': 'owner'}
    client = TestClient(main.app)
    solar = client.post('/research/library', json={
        'title': 'Energía solar fotovoltaica', 'query': 'paneles solares y generación eléctrica',
        'summary': 'Estudio de capacidad instalada y almacenamiento.',
        'sources': [{'title': 'Informe de energía renovable', 'url': 'https://example.org/solar', 'snippet': 'Paneles fotovoltaicos y capacidad solar.'}],
        'evidence': {}
    }).json()['research_id']
    battery = client.post('/research/library', json={
        'title': 'Baterías para almacenamiento', 'query': 'almacenamiento energético',
        'summary': 'Tecnologías de baterías para redes eléctricas.', 'sources': [], 'evidence': {}
    }).json()['research_id']
    return client, solar, battery


def test_ranked_search_prioritizes_title_and_reports_matches(tmp_path, monkeypatch):
    client, solar, battery = setup(tmp_path, monkeypatch)
    try:
        response = client.get('/research/library/search', params={'q': 'energía solar', 'limit': 10})
        assert response.status_code == 200
        data = response.json()
        assert data['method'] == 'weighted_lexical_local'
        assert data['semantic_model'] is False
        assert data['results'][0]['id'] == solar
        assert 'solar' in data['results'][0]['matched_terms']
        assert data['searched'] == 2
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_search_indexes_source_titles_and_summaries(tmp_path, monkeypatch):
    client, solar, _ = setup(tmp_path, monkeypatch)
    try:
        results = client.get('/research/library/search', params={'q': 'fotovoltaicos'}).json()['results']
        assert results and results[0]['id'] == solar
        results = client.get('/research/library/search', params={'q': 'renovable'}).json()['results']
        assert results and results[0]['id'] == solar
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_search_validates_query_and_is_account_scoped(tmp_path, monkeypatch):
    client, solar, _ = setup(tmp_path, monkeypatch)
    try:
        assert client.get('/research/library/search', params={'q': 'a'}).status_code == 422
        main.app.dependency_overrides[main.verificar_acceso] = lambda: {'account_id': 'other'}
        response = client.get('/research/library/search', params={'q': 'solar'})
        assert response.status_code == 200
        assert response.json()['results'] == []
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_search_frontend_uses_ranked_endpoint():
    from pathlib import Path
    html = Path(main.BASE_DIR / 'index.html').read_text(encoding='utf-8')
    assert '/search?' in html
    assert 'Coincidencias:' in html
    assert 'Buscar en toda la biblioteca' in html
