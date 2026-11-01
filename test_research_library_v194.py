"""Pruebas de biblioteca privada de investigaciones v1.94."""
from fastapi.testclient import TestClient
import main


def test_library_requires_authentication():
    with TestClient(main.app) as client:
        response = client.get('/research/library')
    assert response.status_code in (401, 403)


def test_save_list_read_delete_research_is_account_scoped(tmp_path, monkeypatch):
    db = tmp_path / 'research.sqlite3'
    monkeypatch.setattr(main, 'DATABASE_PATH', str(db))
    main.inicializar_db()
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO conversaciones(account_id, conversation_id, title) VALUES('a','c1','Chat')")
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {'account_id': 'a'}
    try:
        with TestClient(main.app) as client:
            saved = client.post('/research/library', json={
                'title': 'Cambio climático', 'query': 'impacto regional',
                'summary': 'Resumen contrastado', 'conversation_id': 'c1',
                'sources': [
                    {'title': 'Fuente válida', 'url': 'https://example.org/a', 'snippet': 'Dato'},
                    {'title': 'URL inválida', 'url': 'javascript:alert(1)'}
                ], 'evidence': {'status': 'partial'}
            })
            assert saved.status_code == 200, saved.text
            rid = saved.json()['research_id']
            listing = client.get('/research/library').json()['investigations']
            assert len(listing) == 1 and listing[0]['source_count'] == 1
            detail = client.get(f'/research/library/{rid}').json()
            assert detail['summary'] == 'Resumen contrastado'
            assert len(detail['sources']) == 1
            assert detail['evidence']['status'] == 'partial'
            assert client.delete(f'/research/library/{rid}').json()['deleted'] is True
            assert client.get(f'/research/library/{rid}').status_code == 404
    finally:
        main.app.dependency_overrides.clear()


def test_research_library_does_not_leak_between_accounts(tmp_path, monkeypatch):
    monkeypatch.setattr(main, 'DATABASE_PATH', str(tmp_path / 'scope.sqlite3'))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {'account_id': 'account_a'}
    try:
        with TestClient(main.app) as client:
            saved = client.post('/research/library', json={'title':'Privado','query':'q'})
            rid = saved.json()['research_id']
    finally:
        main.app.dependency_overrides.clear()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {'account_id': 'account_b'}
    try:
        with TestClient(main.app) as client:
            assert client.get(f'/research/library/{rid}').status_code == 404
            assert client.delete(f'/research/library/{rid}').status_code == 404
    finally:
        main.app.dependency_overrides.clear()
