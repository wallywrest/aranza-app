from fastapi.testclient import TestClient

import main


def test_cors_preflight_allows_put_and_patch_with_auth_headers():
    with TestClient(main.app) as client:
        for method in ("PUT", "PATCH"):
            response = client.options("/profile", headers={
                "Origin": "http://testserver",
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "authorization,content-type",
            })
            assert response.status_code == 200
            assert response.headers.get("access-control-allow-origin") == "http://testserver"
            allowed_methods = {item.strip().upper() for item in response.headers["access-control-allow-methods"].split(",")}
            assert method in allowed_methods
            allowed_headers = response.headers["access-control-allow-headers"].lower()
            assert "authorization" in allowed_headers
            assert "content-type" in allowed_headers
            assert response.headers.get("access-control-allow-credentials") != "true"


def test_cors_rejects_unconfigured_origin():
    with TestClient(main.app) as client:
        response = client.options("/profile", headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "authorization,content-type",
        })
    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None
