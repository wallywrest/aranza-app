"""Pruebas del historial y restauración segura de recuerdos."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"history-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)", (nonce, account_id, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def headers(account_id="owner"):
    return {"Authorization": f"Bearer {token(account_id)}"}


def test_update_records_previous_version_and_restore_preserves_current():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Versión uno", "general", account_id="owner")
    with TestClient(main.app) as client:
        updated = client.put(f"/memory/{memory_id}", json={"content": "Versión dos", "category": "goal"}, headers=headers())
        assert updated.status_code == 200
        history = client.get(f"/memory/{memory_id}/history", headers=headers())
        assert history.status_code == 200
        versions = history.json()["history"]
        assert versions[0]["content"] == "Versión uno"
        assert versions[0]["category"] == "general"
        restored = client.post(f"/memory/{memory_id}/restore/{versions[0]['id']}", headers=headers())
        assert restored.status_code == 200
        current = next(item for item in main.obtener_memorias(account_id="owner") if item["id"] == memory_id)
        assert current["content"] == "Versión uno"
        assert current["category"] == "general"
        latest_history = client.get(f"/memory/{memory_id}/history", headers=headers()).json()["history"]
        assert latest_history[0]["content"] == "Versión dos"


def test_history_requires_authentication():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Privado", "general", account_id="owner")
    with TestClient(main.app) as client:
        assert client.get(f"/memory/{memory_id}/history").status_code == 401


def test_history_and_restore_cannot_cross_accounts():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Otro perfil", "general", account_id="other")
    with TestClient(main.app) as client:
        assert client.get(f"/memory/{memory_id}/history", headers=headers("owner")).status_code == 404
        # Incluso un ID de historial conocido no debe restaurarse a través de cuentas.
        version_id = main.guardar_memoria("Semilla", "general", account_id="owner")
        client.put(f"/memory/{version_id}", json={"content": "Nueva", "category": "general"}, headers=headers("owner"))
        history_id = client.get(f"/memory/{version_id}/history", headers=headers("owner")).json()["history"][0]["id"]
        assert client.post(f"/memory/{memory_id}/restore/{history_id}", headers=headers("other")).status_code == 404
