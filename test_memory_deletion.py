from uuid import uuid4

from fastapi.testclient import TestClient

import main


def _seed_memory_with_private_history(account_id, label):
    memory_id = main.guardar_memoria(f"synthetic memory {label}", "test", account_id=account_id)
    with main.conectar_db() as conn:
        conn.execute(
            "INSERT INTO memoria_historial(memory_id, account_id, category, content) VALUES (?, ?, ?, ?)",
            (memory_id, account_id, "test", f"synthetic old memory {label}"),
        )
        conn.execute(
            "INSERT INTO decisiones_revision_memoria(account_id, memory_id, decision, candidate_content) VALUES (?, ?, ?, ?)",
            (account_id, memory_id, "temporal", f"synthetic candidate {label}"),
        )
    return memory_id


def _counts(account_id):
    with main.conectar_db() as conn:
        return {
            table: conn.execute(f"SELECT COUNT(*) FROM {table} WHERE account_id = ?", (account_id,)).fetchone()[0]
            for table in ("memorias", "memoria_historial", "decisiones_revision_memoria")
        }


def test_deleting_one_memory_removes_its_history_and_review_decisions_only():
    main.inicializar_db()
    suffix = uuid4().hex
    account_id = f"memory-delete-{suffix}"
    other_account_id = f"memory-keep-{suffix}"
    memory_id = _seed_memory_with_private_history(account_id, suffix)
    other_memory_id = _seed_memory_with_private_history(other_account_id, suffix)
    token = main.crear_token_sesion(account_id)

    with TestClient(main.app) as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete(f"/memory/{memory_id}", headers=headers)
        assert response.status_code == 200
        assert client.get(f"/memory/{memory_id}/history", headers=headers).status_code == 404
        assert all(item["memory_id"] != memory_id for item in client.get(
            "/memory/review-decisions", headers=headers
        ).json()["decisions"])
        exported = client.get("/export", headers=headers).json()

    assert exported["memories"] == []
    assert exported["memory_history"] == []
    assert exported["memory_review_decisions"] == []
    assert _counts(account_id) == {"memorias": 0, "memoria_historial": 0, "decisiones_revision_memoria": 0}
    assert _counts(other_account_id) == {"memorias": 1, "memoria_historial": 1, "decisiones_revision_memoria": 1}
    assert main.obtener_memorias(account_id=other_account_id)[0]["id"] == other_memory_id


def test_deleting_all_memories_removes_all_private_history_but_preserves_other_account():
    main.inicializar_db()
    suffix = uuid4().hex
    account_id = f"memory-delete-all-{suffix}"
    other_account_id = f"memory-keep-all-{suffix}"
    memory_ids = [
        _seed_memory_with_private_history(account_id, f"{suffix}-{index}")
        for index in range(2)
    ]
    other_memory_id = _seed_memory_with_private_history(other_account_id, suffix)
    token = main.crear_token_sesion(account_id)

    with TestClient(main.app) as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("/memory", headers=headers)
        assert response.status_code == 200
        assert response.json()["deleted_all_memories"] is True
        for memory_id in memory_ids:
            assert client.get(f"/memory/{memory_id}/history", headers=headers).status_code == 404
        exported = client.get("/export", headers=headers).json()

    assert exported["memories"] == []
    assert exported["memory_history"] == []
    assert exported["memory_review_decisions"] == []
    assert _counts(account_id) == {"memorias": 0, "memoria_historial": 0, "decisiones_revision_memoria": 0}
    assert _counts(other_account_id) == {"memorias": 1, "memoria_historial": 1, "decisiones_revision_memoria": 1}
    assert main.obtener_memorias(account_id=other_account_id)[0]["id"] == other_memory_id
