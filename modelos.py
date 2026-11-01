"""Enrutador pequeño de modelos para Aranza.

Usa el formato de chat completions compatible con OpenAI. Esto permite conectar
proveedores compatibles sin acoplar la lógica conversacional a un SDK específico.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx

logger = logging.getLogger("aranza.modelos")


@dataclass(frozen=True)
class ProveedorModelo:
    nombre: str
    base_url: str
    api_key: str
    modelo: str
    timeout: float = 45.0

    @property
    def configurado(self) -> bool:
        return bool(self.base_url and self.api_key and self.modelo)

    @property
    def endpoint(self) -> str:
        return self.base_url.rstrip("/") + "/chat/completions"


class ErrorEnrutamientoModelo(RuntimeError):
    """Todos los proveedores configurados fallaron o no hay credenciales."""


def proveedores_configurados() -> list[ProveedorModelo]:
    """Lee configuración de entorno; las claves nunca se registran en logs."""
    primaria = ProveedorModelo(
        nombre=os.getenv("ARANZA_PRIMARY_PROVIDER", "groq"),
        base_url=os.getenv("ARANZA_PRIMARY_BASE_URL", "https://api.groq.com/openai/v1"),
        api_key=os.getenv("ARANZA_PRIMARY_API_KEY", os.getenv("GROQ_API_KEY", "")).strip(),
        modelo=os.getenv("ARANZA_PRIMARY_MODEL", os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")).strip().strip('"').strip("'"),
        timeout=float(os.getenv("ARANZA_MODEL_TIMEOUT_SECONDS", "45")),
    )
    lista = [primaria] if primaria.configurado else []

    # El respaldo se configura por separado. Si no se define, conserva el
    # comportamiento histórico de usar otro modelo en el mismo proveedor Groq.
    fallback_key = os.getenv("ARANZA_FALLBACK_API_KEY", os.getenv("GROQ_API_KEY", "")).strip()
    fallback_base = os.getenv("ARANZA_FALLBACK_BASE_URL", primaria.base_url).strip()
    fallback_model = os.getenv("ARANZA_FALLBACK_MODEL", "llama-3.1-8b-instant").strip()
    fallback_name = os.getenv("ARANZA_FALLBACK_PROVIDER", primaria.nombre).strip()
    fallback = ProveedorModelo(
        nombre=fallback_name,
        base_url=fallback_base,
        api_key=fallback_key,
        modelo=fallback_model,
        timeout=float(os.getenv("ARANZA_MODEL_TIMEOUT_SECONDS", "45")),
    )
    if fallback.configurado and not any(
        p.base_url.rstrip("/") == fallback.base_url.rstrip("/") and p.modelo == fallback.modelo
        for p in lista
    ):
        lista.append(fallback)
    return lista


async def completar_chat(
    mensajes: list[dict[str, str]],
    *,
    temperatura: float,
    max_tokens: int,
    proveedores: Optional[list[ProveedorModelo]] = None,
    transport: Optional[httpx.AsyncBaseTransport] = None,
) -> tuple[str, dict[str, Any]]:
    """Prueba proveedores en orden y devuelve contenido + metadatos no secretos."""
    opciones = proveedores if proveedores is not None else proveedores_configurados()
    if not opciones:
        raise ErrorEnrutamientoModelo(
            "No hay modelos configurados. Define una clave API y un proveedor compatible."
        )

    errores: list[str] = []
    for proveedor in opciones:
        try:
            headers = {
                "Authorization": f"Bearer {proveedor.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": proveedor.modelo,
                "messages": mensajes,
                "temperature": temperatura,
                "max_tokens": max_tokens,
            }
            async with httpx.AsyncClient(timeout=proveedor.timeout, transport=transport) as session:
                response = await session.post(proveedor.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            contenido = data["choices"][0]["message"].get("content") or ""
            if not isinstance(contenido, str) or not contenido.strip():
                raise ValueError("El proveedor devolvió una respuesta vacía.")
            return contenido, {"provider": proveedor.nombre, "model": proveedor.modelo}
        except Exception as exc:  # fallo de red, HTTP o formato del proveedor
            errores.append(f"{proveedor.nombre}/{proveedor.modelo}: {type(exc).__name__}")
            logger.warning("Proveedor de modelo falló (%s/%s): %s", proveedor.nombre, proveedor.modelo, type(exc).__name__)

    raise ErrorEnrutamientoModelo("Todos los proveedores configurados fallaron: " + "; ".join(errores))


def proveedores_para_tarea(tarea: str) -> list[ProveedorModelo]:
    """Devuelve proveedor especializado opcional seguido de la cadena general.

    Variables por tarea: ARANZA_ANALYSIS_PROVIDER/BASE_URL/API_KEY/MODEL,
    ARANZA_CODING_*, ARANZA_MATH_* y ARANZA_WRITING_*.
    Si no hay configuración especializada, se usa la cadena general.
    """
    prefijos = {
        "analysis": "ARANZA_ANALYSIS",
        "coding": "ARANZA_CODING",
        "math": "ARANZA_MATH",
        "writing": "ARANZA_WRITING",
    }
    base = proveedores_configurados()
    prefijo = prefijos.get(tarea)
    if not prefijo:
        return base

    primary = base[0] if base else None
    specialized = ProveedorModelo(
        nombre=os.getenv(f"{prefijo}_PROVIDER", f"{tarea}-specialist").strip(),
        base_url=os.getenv(f"{prefijo}_BASE_URL", "").strip(),
        api_key=os.getenv(f"{prefijo}_API_KEY", "").strip(),
        modelo=os.getenv(f"{prefijo}_MODEL", "").strip(),
        timeout=float(os.getenv("ARANZA_MODEL_TIMEOUT_SECONDS", "45")),
    )
    if not specialized.configurado:
        return base

    cadena = [specialized]
    for proveedor in base:
        if (proveedor.base_url.rstrip("/") != specialized.base_url.rstrip("/")
                or proveedor.modelo != specialized.modelo):
            cadena.append(proveedor)
    return cadena


def proveedor_vision_configurado() -> Optional[ProveedorModelo]:
    """Proveedor multimodal explícito; no asume que el modelo de chat vea imágenes."""
    proveedor = ProveedorModelo(
        nombre=os.getenv("ARANZA_VISION_PROVIDER", "vision-provider").strip(),
        base_url=os.getenv("ARANZA_VISION_BASE_URL", "").strip(),
        api_key=os.getenv("ARANZA_VISION_API_KEY", "").strip(),
        modelo=os.getenv("ARANZA_VISION_MODEL", "").strip(),
        timeout=float(os.getenv("ARANZA_VISION_TIMEOUT_SECONDS", os.getenv("ARANZA_MODEL_TIMEOUT_SECONDS", "60"))),
    )
    return proveedor if proveedor.configurado else None


async def completar_vision(mensajes: list[dict[str, Any]], *, temperatura: float, max_tokens: int, transport: Optional[httpx.AsyncBaseTransport] = None) -> tuple[str, dict[str, Any]]:
    """Envía contenido multimodal solo a un proveedor configurado expresamente."""
    proveedor = proveedor_vision_configurado()
    if not proveedor:
        raise ErrorEnrutamientoModelo("No hay un proveedor de visión configurado.")
    return await completar_chat(mensajes, temperatura=temperatura, max_tokens=max_tokens, proveedores=[proveedor], transport=transport)


def resumen_configuracion_modelos() -> dict[str, Any]:
    """Resumen seguro de modelos configurados; nunca devuelve claves ni URLs."""
    generales = proveedores_configurados()
    tareas = ("analysis", "coding", "math", "writing")
    rutas: dict[str, list[dict[str, str]]] = {}
    for tarea in tareas:
        rutas[tarea] = [
            {"provider": proveedor.nombre, "model": proveedor.modelo,
             "role": "specialized" if i == 0 and len(proveedores_para_tarea(tarea)) > len(generales) else ("primary" if i == 0 else "fallback")}
            for i, proveedor in enumerate(proveedores_para_tarea(tarea))
        ]
    return {
        "configured": bool(generales),
        "provider_count": len(generales),
        "providers": [
            {"provider": proveedor.nombre, "model": proveedor.modelo,
             "role": "primary" if i == 0 else "fallback"}
            for i, proveedor in enumerate(generales)
        ],
        "task_routes": rutas,
        "vision_configured": proveedor_vision_configurado() is not None,
        "secrets_exposed": False,
    }
