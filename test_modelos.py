import httpx
import pytest

from modelos import ProveedorModelo, completar_chat, ErrorEnrutamientoModelo


@pytest.mark.anyio
async def test_enrutador_usa_proveedor_y_devuelve_metadatos():
    llamadas = []

    def handler(request):
        llamadas.append((str(request.url), request.headers.get("authorization"), request.read()))
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "Respuesta simulada de Aranza"}}]
        })

    transporte = httpx.MockTransport(handler)
    proveedores = [ProveedorModelo("prueba", "https://modelo.example/v1", "clave-falsa", "modelo-prueba")]
    respuesta, meta = await completar_chat(
        [{"role": "user", "content": "Hola"}],
        temperatura=0.2,
        max_tokens=100,
        proveedores=proveedores,
        transport=transporte,
    )

    assert respuesta == "Respuesta simulada de Aranza"
    assert meta == {"provider": "prueba", "model": "modelo-prueba"}
    assert llamadas[0][0] == "https://modelo.example/v1/chat/completions"
    assert llamadas[0][1] == "Bearer clave-falsa"
    assert b'"model":"modelo-prueba"' in llamadas[0][2]


@pytest.mark.anyio
async def test_enrutador_prueba_respaldo_si_primario_falla():
    def handler(request):
        if "primary.example" in str(request.url):
            return httpx.Response(503, json={"error": "temporal"})
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "Respuesta de respaldo"}}]
        })

    proveedores = [
        ProveedorModelo("primario", "https://primary.example/v1", "key1", "modelo1", timeout=1),
        ProveedorModelo("respaldo", "https://fallback.example/v1", "key2", "modelo2", timeout=1),
    ]
    respuesta, meta = await completar_chat(
        [{"role": "user", "content": "Hola"}],
        temperatura=0.2,
        max_tokens=100,
        proveedores=proveedores,
        transport=httpx.MockTransport(handler),
    )
    assert respuesta == "Respuesta de respaldo"
    assert meta["provider"] == "respaldo"


@pytest.mark.anyio
async def test_enrutador_informa_error_si_todos_fallan():
    def handler(request):
        return httpx.Response(401, json={"error": "no autorizado"})

    with pytest.raises(ErrorEnrutamientoModelo):
        await completar_chat(
            [{"role": "user", "content": "Hola"}],
            temperatura=0.2,
            max_tokens=100,
            proveedores=[ProveedorModelo("caido", "https://modelo.example/v1", "key", "modelo")],
            transport=httpx.MockTransport(handler),
        )
