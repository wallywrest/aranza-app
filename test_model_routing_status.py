from modelos import ProveedorModelo, resumen_configuracion_modelos


def test_resumen_modelos_no_expone_secretos(monkeypatch):
    monkeypatch.setattr("modelos.proveedores_configurados", lambda: [
        ProveedorModelo("primary", "https://private.example/v1", "super-secret", "model-a"),
        ProveedorModelo("backup", "https://private2.example/v1", "another-secret", "model-b"),
    ])
    monkeypatch.setattr("modelos.proveedores_para_tarea", lambda task: [
        ProveedorModelo("primary", "https://private.example/v1", "super-secret", "model-a")
    ])
    monkeypatch.setattr("modelos.proveedor_vision_configurado", lambda: None)
    result = resumen_configuracion_modelos()
    serialized = repr(result)
    assert result["configured"] is True
    assert result["provider_count"] == 2
    assert result["providers"][0]["role"] == "primary"
    assert result["providers"][1]["role"] == "fallback"
    assert "super-secret" not in serialized
    assert "private.example" not in serialized
    assert result["secrets_exposed"] is False


def test_resumen_sin_proveedores(monkeypatch):
    monkeypatch.setattr("modelos.proveedores_configurados", lambda: [])
    monkeypatch.setattr("modelos.proveedores_para_tarea", lambda task: [])
    monkeypatch.setattr("modelos.proveedor_vision_configurado", lambda: None)
    result = resumen_configuracion_modelos()
    assert result["configured"] is False
    assert result["provider_count"] == 0
    assert result["vision_configured"] is False
