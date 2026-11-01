import verificar_android


def test_accepts_https_backend_and_exact_origins():
    env = {'ARANZA_API_BASE': 'https://api.example.com', 'ARANZA_ALLOWED_ORIGINS': 'https://aranza.example.com,https://localhost'}
    assert all(x['ok'] for x in verificar_android.revisar_android(env))


def test_rejects_http_backend():
    env = {'ARANZA_API_BASE': 'http://api.example.com', 'ARANZA_ALLOWED_ORIGINS': 'https://aranza.example.com'}
    result = {x['name']: x for x in verificar_android.revisar_android(env)}
    assert not result['ARANZA_API_BASE']['ok']


def test_rejects_wildcard_and_path_origins():
    for origin in ('*', 'https://aranza.example.com/app'):
        env = {'ARANZA_API_BASE': 'https://api.example.com', 'ARANZA_ALLOWED_ORIGINS': origin}
        result = {x['name']: x for x in verificar_android.revisar_android(env)}
        assert not result['ARANZA_ALLOWED_ORIGINS']['ok']


def test_rejects_embedded_credentials_and_query_in_api_url():
    for api in ('https://user:pass@api.example.com', 'https://api.example.com?key=secret'):
        env = {'ARANZA_API_BASE': api, 'ARANZA_ALLOWED_ORIGINS': 'https://aranza.example.com'}
        result = {x['name']: x for x in verificar_android.revisar_android(env)}
        assert not result['ARANZA_API_BASE']['ok']
