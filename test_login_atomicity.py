"""Pruebas de límite persistente y atómico del inicio de sesión."""
import main
from fastapi.testclient import TestClient


def test_login_attempt_limit_persists_in_sqlite():
    client_id = "test-persistent-lockout"
    with main.conectar_db() as conn:
        conn.execute("DELETE FROM intentos_login WHERE client_id = ?", (client_id,))

    for _ in range(main.LOGIN_MAX_ATTEMPTS):
        assert main.validar_login_atomico(client_id, "owner", "incorrecta") is None

    try:
        main.validar_login_atomico(client_id, "owner", "test-password-123")
    except Exception as exc:
        from fastapi import HTTPException
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 429
    else:
        raise AssertionError("El límite de intentos debía bloquear el acceso")


def test_successful_login_clears_previous_failures():
    client_id = "test-clear-lockout"
    with main.conectar_db() as conn:
        conn.execute("DELETE FROM intentos_login WHERE client_id = ?", (client_id,))
    assert main.validar_login_atomico(client_id, "owner", "incorrecta") is None
    assert main.validar_login_atomico(client_id, "owner", "test-password-123") == "owner"
    with main.conectar_db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM intentos_login WHERE client_id = ?", (client_id,)
        ).fetchone()[0]
    assert count == 0


def test_login_endpoint_returns_429_after_limit():
    with TestClient(main.app) as client:
        for _ in range(main.LOGIN_MAX_ATTEMPTS):
            response = client.post("/login", json={"password": "bad-password"})
            assert response.status_code == 401
        response = client.post("/login", json={"password": "test-password-123"})
        assert response.status_code == 429
