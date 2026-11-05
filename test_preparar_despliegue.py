import preparar_despliegue


def test_preflight_accepts_production_like_configuration():
    env = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
        "ARANZA_USERNAME": "melvis_test",
    }
    assert all(item["ok"] for item in preparar_despliegue.revisar(env))


def test_preflight_flags_missing_secrets_and_insecure_origin():
    env = {"ARANZA_PASSWORD": "", "ARANZA_SESSION_SECRET": "", "ARANZA_ALLOWED_ORIGINS": "*"}
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert not results["ARANZA_PASSWORD"]["ok"]
    assert not results["ARANZA_SESSION_SECRET"]["ok"]
    assert not results["ARANZA_ALLOWED_ORIGINS"]["ok"]


def test_preflight_warns_if_no_model_provider_is_configured():
    env = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
    }
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert not results["GROQ_API_KEY"]["ok"]
    assert results["GROQ_API_KEY"]["severity"] == "ERROR"


def test_preflight_rejects_database_outside_render_persistent_disk():
    env = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
    }
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert not results["ARANZA_DB_PATH"]["ok"]


def test_preflight_accepts_render_persistent_disk_path():
    env = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
    }
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert results["ARANZA_DB_PATH"]["ok"]


def test_preflight_rejects_session_secret_equal_to_password():
    env = {
        "ARANZA_PASSWORD": "same-secret-for-test-123",
        "ARANZA_SESSION_SECRET": "same-secret-for-test-123",
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
        "ARANZA_USERNAME": "melvis_test",
    }
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert not results["ARANZA_SESSION_SECRET"]["ok"]


def test_preflight_rejects_example_session_secret():
    env = {
        "ARANZA_PASSWORD": "a-different-secure-password",
        "ARANZA_SESSION_SECRET": "change-me",
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
        "ARANZA_USERNAME": "melvis_test",
    }
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert not results["ARANZA_SESSION_SECRET"]["ok"]


def test_preflight_rejects_origin_with_path_or_duplicates():
    base = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
        "ARANZA_USERNAME": "melvis_test",
    }
    for origins in ("https://aranza.example.com/app", "https://aranza.example.com,https://aranza.example.com"):
        results = {item["name"]: item for item in preparar_despliegue.revisar({**base, "ARANZA_ALLOWED_ORIGINS": origins})}
        assert not results["ARANZA_ALLOWED_ORIGINS"]["ok"]


def test_preflight_warns_on_default_username():
    env = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "ARANZA_DB_PATH": "/var/data/aranza.sqlite3",
        "GROQ_API_KEY": "test-provider-key",
        "ARANZA_USERNAME": "owner",
    }
    results = {item["name"]: item for item in preparar_despliegue.revisar(env)}
    assert not results["ARANZA_USERNAME"]["ok"]
    assert results["ARANZA_USERNAME"]["severity"] == "WARNING"


def test_preflight_rejects_windows_path_and_path_traversal():
    base = {
        "ARANZA_PASSWORD": "una-clave-segura-de-prueba",
        "ARANZA_SESSION_SECRET": "x" * 48,
        "ARANZA_ALLOWED_ORIGINS": "https://aranza.example.com",
        "GROQ_API_KEY": "test-provider-key",
    }
    windows_path = preparar_despliegue.revisar({
        **base, "ARANZA_DB_PATH": r"C:\var\data\aranza.sqlite3",
    })
    traversal_path = preparar_despliegue.revisar({
        **base, "ARANZA_DB_PATH": "/var/data/../etc/aranza.sqlite3",
    })
    assert not next(item for item in windows_path if item["name"] == "ARANZA_DB_PATH")["ok"]
    assert not next(item for item in traversal_path if item["name"] == "ARANZA_DB_PATH")["ok"]
