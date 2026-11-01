"""Registro y contratos de herramientas ejecutables de Aranza.

El registro describe capacidades; la ejecución real permanece en el backend,
con autenticación, validación por herramienta y sin aceptar nombres arbitrarios.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolContract:
    name: str
    description: str
    input_fields: tuple[str, ...]
    read_only: bool = True
    requires_confirmation: bool = False


TOOLS: dict[str, ToolContract] = {
    "web_search": ToolContract(
        "web_search", "Busca fuentes públicas en la web.", ("query", "limit")
    ),
    "web_research": ToolContract(
        "web_research", "Busca fuentes y lee hasta dos páginas públicas.", ("query", "limit")
    ),
    "read_webpage": ToolContract(
        "read_webpage", "Extrae texto de una página pública validada.", ("url",)
    ),
    "file_analysis": ToolContract(
        "file_analysis", "Analiza un archivo adjunto mediante endpoint dedicado.", ("file", "instruction")
    ),
    "vision": ToolContract(
        "vision", "Analiza una imagen adjunta mediante endpoint dedicado.", ("file", "instruction")
    ),
}


class ToolInputError(ValueError):
    pass


def validate_tool_request(payload: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ToolInputError("Se esperaba un objeto JSON.")
    name = payload.get("name")
    if not isinstance(name, str) or name not in TOOLS:
        raise ToolInputError("Herramienta desconocida o no habilitada.")
    arguments = payload.get("arguments", {})
    if not isinstance(arguments, dict):
        raise ToolInputError("Los argumentos deben ser un objeto JSON.")
    contract = TOOLS[name]
    unknown = set(arguments) - set(contract.input_fields)
    if unknown:
        raise ToolInputError("La solicitud contiene argumentos no permitidos.")
    if name in {"web_search", "web_research"}:
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip() or len(query) > 300:
            raise ToolInputError("La consulta debe contener entre 1 y 300 caracteres.")
        limit = arguments.get("limit", 5)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 5:
            raise ToolInputError("El límite debe ser un entero entre 1 y 5.")
        arguments = {"query": " ".join(query.split()), "limit": limit}
    elif name == "read_webpage":
        url = arguments.get("url")
        if not isinstance(url, str) or not url.strip() or len(url) > 2000:
            raise ToolInputError("Se requiere una URL válida de hasta 2000 caracteres.")
        arguments = {"url": url.strip()}
    else:
        # Los adjuntos requieren multipart/form-data y se mantienen en sus
        # endpoints dedicados. No se aceptan como JSON ni se almacenan aquí.
        raise ToolInputError("Esta herramienta requiere un archivo adjunto y debe usarse desde su endpoint dedicado.")
    return name, arguments


def list_tool_contracts() -> list[dict[str, Any]]:
    return [
        {"name": item.name, "description": item.description,
         "read_only": item.read_only,
         "requires_confirmation": item.requires_confirmation,
         "execution_mode": "unified" if item.name in {"web_search", "web_research", "read_webpage"} else "dedicated_upload"}
        for item in TOOLS.values()
    ]
