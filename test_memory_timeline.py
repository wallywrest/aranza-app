"""Pruebas para la línea temporal de recuerdos."""
import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient
import main


def token(account_id="owner"):
    expires_at = int(time.time()) + main.SESSION_TTL_SECONDS
    nonce = f"timeline-{account_id}-{time.time_ns()}"
    with main.conectar_db() as conn:
        conn.execute("INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)", (nonce, account_id, expires_at))
    payload = json.dumps({"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(hmac.new(main._session_secret(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
    return f"{body}.{signature}"


def headers(account_id="owner"):
    return {"Authorization": f"Bearer {token(account_id)}"}


def test_timeline_includes_current_and_previous_versions():
    main.inicializar_db()
    memory_id = main.guardar_memoria("Preferencia antigua", "preference", account_id="owner")
    with TestClient(main.app) as client:
        response = client.put(f"/memory/{memory_id}", json={"content": "Preferencia actual", "category": "preference"}, headers=headers())
        assert response.status_code == 200
        timeline = client.get("/memory/timeline", headers=headers())
    assert timeline.status_code == 200
    events = [event for event in timeline.json()["events"] if event["memory_id"] == memory_id]
    assert {event["event_type"] for event in events} == {"current", "previous_version"}
    assert any(event["content"] == "Preferencia antigua" for event in events)
    assert any(event["content"] == "Preferencia actual" for event in events)


def test_timeline_is_account_scoped():
    main.inicializar_db()
    main.guardar_memoria("Solo cuenta privada", "personal", account_id="timeline-private")
    with TestClient(main.app) as client:
        response = client.get("/memory/timeline", headers=headers("timeline-other"))
    assert response.status_code == 200
    assert all(event["content"] != "Solo cuenta privada" for event in response.json()["events"])


def test_timeline_limit_is_clamped():
    main.inicializar_db()
    with TestClient(main.app) as client:
        response = client.get("/memory/timeline?limit=9999", headers=headers())
    assert response.status_code == 200
    assert response.json()["limit"] == 200
