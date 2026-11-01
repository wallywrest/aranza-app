from fastapi.testclient import TestClient
import main


def test_edit_research_saves_snapshot_and_restore_is_reversible(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "DATABASE_PATH", str(tmp_path / "history.sqlite3"))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    with TestClient(main.app) as client:
        saved = client.post("/research/library", json={"title":"Tema original", "query":"consulta original", "summary":"resumen original", "sources":[], "evidence":{"v":1}})
        rid = saved.json()["research_id"]
        changed = client.put(f"/research/library/{rid}", json={"title":"Tema nuevo", "query":"consulta nueva", "summary":"resumen nuevo", "sources":[], "evidence":{"v":2}})
        assert changed.status_code == 200 and changed.json()["snapshot_saved"]
        history = client.get(f"/research/library/{rid}/history").json()["history"]
        old_version = history[0]["id"]
        restored = client.post(f"/research/library/{rid}/history/{old_version}/restore")
        assert restored.status_code == 200
        detail = client.get(f"/research/library/{rid}").json()
        assert detail["title"] == "Tema original"
        assert detail["summary"] == "resumen original"
        assert detail["evidence"] == {"v": 1}
        assert len(client.get(f"/research/library/{rid}/history").json()["history"]) == 2
    main.app.dependency_overrides.clear()


def test_research_history_cannot_cross_accounts(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "DATABASE_PATH", str(tmp_path / "isolation.sqlite3"))
    main.inicializar_db()
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    with TestClient(main.app) as client:
        saved = client.post("/research/library", json={"title":"Privado", "query":"q", "summary":"s", "sources":[], "evidence":{}})
        rid = saved.json()["research_id"]
        client.put(f"/research/library/{rid}", json={"title":"Editado", "query":"q", "summary":"s", "sources":[], "evidence":{}})
        history_id = client.get(f"/research/library/{rid}/history").json()["history"][0]["id"]
        main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "other"}
        assert client.post(f"/research/library/{rid}/history/{history_id}/restore").status_code == 404
    main.app.dependency_overrides.clear()
