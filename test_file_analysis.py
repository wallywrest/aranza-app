import asyncio
from fastapi.testclient import TestClient
import main


def test_extracts_utf8_text_without_persisting_files():
    text = main.extraer_texto_archivo("notas.md", "# Ideas\nTexto útil".encode())
    assert text == "# Ideas\nTexto útil"
    assert not (main.BASE_DIR / "notas.md").exists()


def test_rejects_unsupported_or_empty_files():
    import pytest
    with pytest.raises(ValueError, match="Formato no admitido"):
        main.extraer_texto_archivo("programa.exe", b"MZ")
    with pytest.raises(ValueError, match="vacío"):
        main.extraer_texto_archivo("notas.txt", b"")


def test_rejects_oversized_file():
    import pytest
    with pytest.raises(ValueError, match="5 MB"):
        main.extraer_texto_archivo("notas.txt", b"x" * (main.MAX_FILE_BYTES + 1))


def test_file_analysis_requires_authentication():
    with TestClient(main.app) as client:
        response = client.post("/tools/analyze-file", files={"file": ("notas.txt", b"hola", "text/plain")})
    assert response.status_code in (401, 403)


def test_analyze_file_calls_model_and_does_not_persist(monkeypatch):
    main.app.dependency_overrides[main.verificar_acceso] = lambda: {"account_id": "owner"}
    async def fake_complete(messages, **kwargs):
        assert "contenido no confiable" in messages[0]["content"]
        assert "Texto de prueba" in messages[1]["content"]
        return "Resumen de prueba", {"provider": "test", "model": "test-model"}
    monkeypatch.setattr(main, "completar_chat", fake_complete)
    monkeypatch.setattr(main, "construir_prompt", lambda memories: "Sistema de prueba")
    monkeypatch.setattr(main, "obtener_memorias", lambda **kwargs: [])
    monkeypatch.setattr(main, "preparar_ruta", lambda instruction: type("Route", (), {"proveedores": []})())
    try:
        with TestClient(main.app) as client:
            response = client.post(
                "/tools/analyze-file",
                files={"file": ("notas.txt", "Texto de prueba".encode(), "text/plain")},
                data={"instruction": "Resume el archivo"},
            )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["response"] == "Resumen de prueba"
        assert payload["stored"] is False
        assert payload["characters_extracted"] == len("Texto de prueba")
    finally:
        main.app.dependency_overrides.clear()


def test_image_validation_accepts_valid_jpeg_without_saving():
    assert main.validar_imagen("foto.jpg", b"\xff\xd8\xffdatos", "image/jpeg") == "image/jpeg"


def test_image_validation_rejects_mime_mismatch_and_oversized_payload():
    import pytest
    with pytest.raises(ValueError, match="no coincide"):
        main.validar_imagen("foto.png", b"\xff\xd8\xffdatos", "image/png")
    with pytest.raises(ValueError, match="5 MB"):
        main.validar_imagen("foto.jpg", b"\xff\xd8\xff" + b"x" * main.MAX_IMAGE_BYTES, "image/jpeg")


def test_image_analysis_requires_authentication():
    with TestClient(main.app) as client:
        response = client.post("/tools/analyze-image", files={"file": ("foto.jpg", b"\xff\xd8\xffdatos", "image/jpeg")})
    assert response.status_code in (401, 403)
