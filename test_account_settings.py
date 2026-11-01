"""Pruebas para ajustes de cuenta y encabezados de seguridad."""
import main
from fastapi.testclient import TestClient


def setup_function():
    # Aísla estas pruebas del orden de ejecución del conjunto completo.
    main.inicializar_db()
    salt, digest = main.generar_hash_contrasena("test-password-123")
    with main.conectar_db() as conn:
        conn.execute("UPDATE cuentas SET username='owner', password_salt=?, password_hash=?, password_iterations=? WHERE account_id='owner'",
                     (salt, digest, main.PASSWORD_HASH_ITERATIONS))
        conn.execute("DELETE FROM sesiones")
        conn.execute("DELETE FROM intentos_login")
    main._login_attempts.clear()


def _login(client, password="test-password-123", username="owner"):
    response = client.post("/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_change_username_revalidates_password_and_revokes_sessions():
    with TestClient(main.app) as client:
        headers_a = _login(client)
        headers_b = _login(client)
        response = client.post("/change-username", headers=headers_a, json={
            "current_password": "test-password-123", "new_username": "melvis_aranza"
        })
        assert response.status_code == 200
        assert response.json()["username"] == "melvis_aranza"
        assert response.json()["sessions_revoked"] is True
        assert client.get("/session", headers=headers_a).status_code == 401
        assert client.get("/session", headers=headers_b).status_code == 401
        assert client.post("/login", json={"username": "owner", "password": "test-password-123"}).status_code == 401
        assert client.post("/login", json={"username": "melvis_aranza", "password": "test-password-123"}).status_code == 200


def test_change_username_requires_current_password():
    with TestClient(main.app) as client:
        headers = _login(client)
        response = client.post("/change-username", headers=headers, json={
            "current_password": "incorrecta", "new_username": "otro_usuario"
        })
        assert response.status_code == 401
        with main.conectar_db() as conn:
            row = conn.execute("SELECT username FROM cuentas WHERE account_id='owner'").fetchone()
        assert row["username"] == "owner"


def test_change_username_rejects_invalid_and_same_username():
    with TestClient(main.app) as client:
        headers = _login(client)
        invalid = client.post("/change-username", headers=headers, json={
            "current_password": "test-password-123", "new_username": "x"
        })
        same = client.post("/change-username", headers=headers, json={
            "current_password": "test-password-123", "new_username": "OWNER"
        })
        assert invalid.status_code == 422
        assert same.status_code == 400


def test_security_headers_are_present():
    with TestClient(main.app) as client:
        response = client.get("/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
