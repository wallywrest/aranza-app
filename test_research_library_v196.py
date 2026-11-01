from fastapi.testclient import TestClient
import main


def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DATABASE_PATH', str(tmp_path / 'library-v196.sqlite3'))
    main.inicializar_db()
    account = {'account_id': 'owner'}
    main.app.dependency_overrides[main.verificar_acceso] = lambda: account
    client = TestClient(main.app)
    a = client.post('/research/library', json={'title':'Energía solar','query':'paneles solares','summary':'Resumen A'}).json()['research_id']
    b = client.post('/research/library', json={'title':'Baterías','query':'almacenamiento','summary':'Resumen B'}).json()['research_id']
    return client, a, b


def test_tags_are_normalized_searchable_and_history_is_saved(tmp_path, monkeypatch):
    client, a, b = setup(tmp_path, monkeypatch)
    try:
        response = client.patch(f'/research/library/{a}/tags', json={'tags':[' Energía ', 'solar', 'ENERGÍA', '']})
        assert response.status_code == 200
        assert response.json()['tags'] == ['Energía', 'solar']
        assert client.get('/research/library', params={'tag':'solar'}).json()['investigations'][0]['id'] == a
        detail = client.get(f'/research/library/{a}').json()
        assert detail['tags'] == ['Energía', 'solar']
        assert len(detail['history']) == 1
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_relations_are_bidirectional_and_account_scoped(tmp_path, monkeypatch):
    client, a, b = setup(tmp_path, monkeypatch)
    try:
        response = client.post(f'/research/library/{a}/relations', json={'related_id':b})
        assert response.status_code == 200
        assert client.get(f'/research/library/{a}').json()['related'][0]['id'] == b
        assert client.get(f'/research/library/{b}').json()['related'][0]['id'] == a
        assert client.post(f'/research/library/{a}/relations', json={'related_id':'missing'}).status_code == 404
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_delete_removes_relations_and_history(tmp_path, monkeypatch):
    client, a, b = setup(tmp_path, monkeypatch)
    try:
        client.patch(f'/research/library/{a}/tags', json={'tags':['x']})
        client.post(f'/research/library/{a}/relations', json={'related_id':b})
        assert client.delete(f'/research/library/{a}').status_code == 200
        assert client.get(f'/research/library/{b}').json()['related'] == []
        with main.conectar_db() as conn:
            assert conn.execute('SELECT COUNT(*) FROM historial_investigacion').fetchone()[0] == 0
            assert conn.execute('SELECT COUNT(*) FROM relaciones_investigacion').fetchone()[0] == 0
    finally:
        client.close(); main.app.dependency_overrides.clear()


def test_library_frontend_exposes_tags_relations_and_history():
    from pathlib import Path
    html = Path(main.BASE_DIR / 'index.html').read_text(encoding='utf-8')
    assert 'Editar etiquetas' in html
    assert 'Relacionar con otro' in html
    assert 'Historial de cambios' in html
