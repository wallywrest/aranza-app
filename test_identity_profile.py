from uuid import uuid4

from fastapi.testclient import TestClient

import main


def _create_test_account():
    suffix = uuid4().hex
    account_id = f"profile-test-{suffix}"
    username = f"profile-{suffix[:16]}"
    password = f"synthetic-password-{suffix[:12]}"
    salt, digest = main.generar_hash_contrasena(password)
    with main.conectar_db() as conn:
        conn.execute(
            """INSERT INTO cuentas(account_id, username, password_salt, password_hash, password_iterations)
               VALUES(?, ?, ?, ?, ?)""",
            (account_id, username, salt, digest, main.PASSWORD_HASH_ITERATIONS),
        )
    return account_id, username, password


def test_profiles_are_isolated_and_do_not_replace_aranza_identity():
    main.inicializar_db()
    first_account = f"profile-first-{uuid4().hex}"
    second_account = f"profile-second-{uuid4().hex}"
    first_token = main.crear_token_sesion(first_account)
    second_token = main.crear_token_sesion(second_account)
    first_profile = {
        "comunicacion_observada": ["synthetic first account marker"],
        "interaccion_observada": ["synthetic first interaction"],
    }
    second_profile = {
        "comunicacion_observada": ["synthetic second account marker"],
    }

    with TestClient(main.app) as client:
        first_headers = {"Authorization": f"Bearer {first_token}"}
        second_headers = {"Authorization": f"Bearer {second_token}"}
        assert client.get("/profile", headers=first_headers).json()["profile"]["comunicacion_observada"] == []
        assert client.put("/profile", headers=first_headers, json=first_profile).status_code == 200
        assert client.put("/profile", headers=second_headers, json=second_profile).status_code == 200
        first_result = client.get("/profile", headers=first_headers).json()["profile"]
        second_result = client.get("/profile", headers=second_headers).json()["profile"]

    assert first_result["comunicacion_observada"] == first_profile["comunicacion_observada"]
    assert second_result["comunicacion_observada"] == second_profile["comunicacion_observada"]
    first_prompt = main.construir_prompt([], account_id=first_account)
    second_prompt = main.construir_prompt([], account_id=second_account)
    assert "synthetic first account marker" in first_prompt
    assert "synthetic second account marker" not in first_prompt
    assert "synthetic second account marker" in second_prompt
    assert "synthetic first account marker" not in second_prompt
    assert "Responde de forma natural, coherente y honesta." in first_prompt
    assert "Responde de forma natural, coherente y honesta." in second_prompt


def test_profile_limits_are_enforced():
    account_id = f"profile-limits-{uuid4().hex}"
    token = main.crear_token_sesion(account_id)
    with TestClient(main.app) as client:
        response = client.put(
            "/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"comunicacion_observada": ["x"] * 21},
        )
    assert response.status_code == 422


def test_account_data_deletion_clears_profile_and_revokes_sessions():
    main.inicializar_db()
    account_id, username, password = _create_test_account()
    token = main.crear_token_sesion(account_id)
    profile = {"comunicacion_observada": ["synthetic profile to erase"]}

    with TestClient(main.app) as client:
        headers = {"Authorization": f"Bearer {token}"}
        assert client.put("/profile", headers=headers, json=profile).status_code == 200
        response = client.request("DELETE", "/account/data", headers=headers, json={
            "current_password": password,
            "confirmation": "ELIMINAR MIS DATOS",
        })
        assert response.status_code == 200
        assert response.json()["deleted_counts"]["profile_reset"] == 1
        assert client.get("/profile", headers=headers).status_code == 401
        login = client.post("/login", json={"username": username, "password": password})
        assert login.status_code == 200
        new_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        main.inicializar_db()
        reset_profile = client.get("/profile", headers=new_headers).json()["profile"]

    assert all(values == [] for values in reset_profile.values())
