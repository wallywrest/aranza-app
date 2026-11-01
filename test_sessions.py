"""Tests de regresión para las sesiones de Aranza v1.2.

Ejecutar desde esta carpeta con: python -m pytest -q
"""
import os
import sys
import types
import tempfile
from pathlib import Path

# Permite probar rutas de autenticación sin instalar ni llamar a Groq.
_groq = types.ModuleType("groq")
class _UnusedAsyncGroq:
    def __init__(self, *args, **kwargs):
        pass
_groq.AsyncGroq = _UnusedAsyncGroq
sys.modules.setdefault("groq", _groq)

_tmp = tempfile.TemporaryDirectory()
os.environ["ARANZA_DB_PATH"] = str(Path(_tmp.name) / "test.sqlite3")
os.environ["ARANZA_PASSWORD"] = "test-password-123"
os.environ["ARANZA_SESSION_SECRET"] = "test-secret-that-is-long-enough-for-unit-tests-123456"
os.environ["ARANZA_ALLOWED_ORIGINS"] = "http://testserver"

import main
from fastapi.testclient import TestClient


def setup_function():
    main._login_attempts.clear()
    main.inicializar_db()
    # Cada prueba empieza con la contraseña de fixture; la aplicación real no
    # vuelve a sincronizarla desde el entorno después del primer arranque.
    salt, digest = main.generar_hash_contrasena("test-password-123")
    with main.conectar_db() as conn:
        conn.execute("UPDATE cuentas SET password_salt=?, password_hash=?, password_iterations=? WHERE account_id='owner'",
                     (salt, digest, main.PASSWORD_HASH_ITERATIONS))
        conn.execute("DELETE FROM intentos_login")
        conn.execute("DELETE FROM sesiones")


def test_login_returns_working_session():
    with TestClient(main.app) as client:
        response = client.post("/login", json={"password": "test-password-123"})
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert client.get("/session", headers={"Authorization": f"Bearer {token}"}).json() == {"authenticated": True}


def test_logout_revokes_token_server_side():
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        assert client.post("/logout", headers=headers).status_code == 200
        assert client.get("/session", headers=headers).status_code == 401


def test_invalid_token_is_rejected():
    with TestClient(main.app) as client:
        response = client.get("/session", headers={"Authorization": "Bearer not-a-valid-token"})
        assert response.status_code == 401


def test_wrong_password_is_rejected():
    with TestClient(main.app) as client:
        response = client.post("/login", json={"username": "owner", "password": "wrong-password"})
        assert response.status_code == 401


def test_password_is_stored_as_hash_not_plaintext():
    with main.conectar_db() as conn:
        account = conn.execute("SELECT password_salt, password_hash, password_iterations FROM cuentas WHERE username='owner'").fetchone()
    assert account is not None
    assert account["password_hash"] != "test-password-123"
    assert account["password_salt"]
    assert account["password_iterations"] >= 200_000


def test_unknown_username_is_rejected_without_leaking_account_existence():
    with TestClient(main.app) as client:
        response = client.post("/login", json={"username": "no-existe", "password": "wrong-password"})
        assert response.status_code == 401
        assert response.json()["detail"] == "El usuario o la contraseña no son correctos."


def test_login_rate_limit_survives_memory_reset():
    with TestClient(main.app) as client:
        for _ in range(main.LOGIN_MAX_ATTEMPTS):
            response = client.post("/login", json={"password": "wrong-password"})
            assert response.status_code == 401
        # Simula reinicio del proceso: el limitador persistente no depende del dict.
        main._login_attempts.clear()
        blocked = client.post("/login", json={"password": "test-password-123"})
        assert blocked.status_code == 429


def test_change_password_revokes_all_sessions_and_requires_new_login():
    with TestClient(main.app) as client:
        token_a = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        token_b = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token_a}"}
        response = client.post("/change-password", headers=headers, json={
            "current_password": "test-password-123",
            "new_password": "a-much-stronger-new-password",
        })
        assert response.status_code == 200
        assert response.json()["sessions_revoked"] is True
        assert client.get("/session", headers=headers).status_code == 401
        assert client.get("/session", headers={"Authorization": f"Bearer {token_b}"}).status_code == 401
        assert client.post("/login", json={"password": "test-password-123"}).status_code == 401
        login = client.post("/login", json={"password": "a-much-stronger-new-password"})
        assert login.status_code == 200
        assert client.get("/session", headers={"Authorization": f"Bearer {login.json()['access_token']}"}).status_code == 200


def test_changed_password_survives_database_reinitialization():
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        response = client.post("/change-password", headers={"Authorization": f"Bearer {token}"}, json={
            "current_password": "test-password-123",
            "new_password": "another-strong-password-2026",
        })
        assert response.status_code == 200
        main.inicializar_db()  # simula el bloque de inicialización de un reinicio
        assert client.post("/login", json={"password": "test-password-123"}).status_code == 401
        assert client.post("/login", json={"password": "another-strong-password-2026"}).status_code == 200


def test_change_password_rejects_wrong_current_password_and_short_new_password():
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        bad_current = client.post("/change-password", headers=headers, json={
            "current_password": "not-the-current-password",
            "new_password": "new-password-long-enough",
        })
        short_new = client.post("/change-password", headers=headers, json={
            "current_password": "test-password-123",
            "new_password": "short",
        })
        assert bad_current.status_code == 401
        assert short_new.status_code == 422
        assert client.post("/login", json={"password": "test-password-123"}).status_code == 200


def test_session_rejected_if_database_account_does_not_match_signed_token():
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        body = token.split(".", 1)[0]
        payload = __import__("json").loads(__import__("base64").urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        with main.conectar_db() as conn:
            conn.execute("UPDATE sesiones SET account_id='different-account' WHERE nonce=?", (payload["nonce"],))
        assert client.get("/session", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_session_rejected_if_database_expiration_does_not_match_token():
    with TestClient(main.app) as client:
        token = client.post("/login", json={"password": "test-password-123"}).json()["access_token"]
        body = token.split(".", 1)[0]
        payload = __import__("json").loads(__import__("base64").urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        with main.conectar_db() as conn:
            conn.execute("UPDATE sesiones SET expires_at=expires_at+60 WHERE nonce=?", (payload["nonce"],))
        assert client.get("/session", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_render_template_requires_explicit_username():
    template = (Path(__file__).parent / "render.yaml").read_text(encoding="utf-8")
    block = template.split("- key: ARANZA_USERNAME", 1)[1].split("- key:", 1)[0]
    assert "sync: false" in block
    assert "value: owner" not in block
