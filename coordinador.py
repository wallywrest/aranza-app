"""Coordinador ligero de tareas para Aranza.

Clasifica por reglas transparentes y selecciona una cadena de proveedores.
No afirma que exista razonamiento multiagente: el enrutamiento es heurístico.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from modelos import ProveedorModelo, proveedores_para_tarea


_NEGACION_INMEDIATA = re.compile(
    r"(?:\bno\s+(?:(?:quiero|quisiera|necesito|deseo)\s+)?(?:que\s+)?"
    r"|\b(?:nunca|jamás|jamas)\s+|\bsin\s+)$",
    flags=re.IGNORECASE,
)


def _intencion_afirmativa(texto: str, patron: str) -> bool:
    """Limita la negación a la cláusula y al disparador inmediatamente posterior."""
    for match in re.finditer(patron, texto, flags=re.IGNORECASE):
        prefijo = texto[:match.start()]
        clausula = re.split(r"[,;.!?\n]", prefijo)[-1]
        if not _NEGACION_INMEDIATA.search(clausula):
            return True
    return False

@dataclass(frozen=True)
class RutaTarea:
    tarea: str
    motivo: str
    proveedores: list[ProveedorModelo]


def clasificar_tarea(mensaje: str) -> tuple[str, str]:
    texto = mensaje.lower().strip()
    if re.search(r"\b(cuánto es|cuanto es|calcula|calcular|resuelve|derivada|integral|ecuación|ecuacion|porcentaje|convierte|conversion|convierte|unidades|notación científica|notacion cientifica)\b", texto):
        return "math", "Se detectaron operaciones, unidades o conceptos matemáticos."
    if re.search(r"\b(código|codigo|programa|programar|debug|depura|error de python|javascript|sql|función en python|funcion en python|api|endpoint|stack trace)\b", texto):
        return "coding", "Se detectó una solicitud de programación o depuración."
    if re.search(r"\b(analiza|analizar|compara|comparar|evalúa|evalua|investiga|investigar|argumenta|argumentar|causas|consecuencias|desglosa|razona)\b", texto):
        return "analysis", "Se detectó una solicitud de análisis o comparación."
    if re.search(r"\b(redacta|escribe|reescribe|corrige|corrige el texto|correo|email|carta|poema|ensayo|resumen|traduce|traducción|traduccion)\b", texto):
        return "writing", "Se detectó una solicitud de escritura o edición."
    return "conversation", "Solicitud general; se usa la configuración predeterminada."


def preparar_ruta(mensaje: str) -> RutaTarea:
    tarea, motivo = clasificar_tarea(mensaje)
    return RutaTarea(tarea=tarea, motivo=motivo, proveedores=proveedores_para_tarea(tarea))


@dataclass(frozen=True)
class HerramientaPlaneada:
    """Herramienta candidata; planear no equivale a ejecutarla."""
    nombre: str
    motivo: str
    requiere_confirmacion: bool = False


def planificar_herramientas(mensaje: str) -> dict:
    """Genera un plan determinista y seguro para la solicitud actual.

    No ejecuta herramientas ni realiza acciones externas. Las operaciones con
    efectos secundarios se marcan para confirmación explícita del usuario.
    """
    texto = mensaje.lower().strip()
    candidatas: list[HerramientaPlaneada] = []

    if _intencion_afirmativa(
        texto, r"\b(investiga|investigues|investiguen|investigando|investigar|investigación|investigacion|compara fuentes|revisión bibliográfica|revision bibliografica)\b"
    ):
        candidatas.append(HerramientaPlaneada(
            "web_research", "La solicitud requiere buscar fuentes y leer una muestra limitada de páginas públicas."
        ))
    elif _intencion_afirmativa(
        texto, r"\b(busca|buscar|fuentes|referencias|actualidad|último|ultima|hoy|reciente|precio actual|noticias)\b"
    ):
        candidatas.append(HerramientaPlaneada(
            "web_search", "La solicitud parece requerir información externa o actualizada."
        ))
    if re.search(r"\b(archivo|documento|pdf|hoja de cálculo|excel|csv|adjunto)\b", texto):
        candidatas.append(HerramientaPlaneada(
            "file_analysis", "La solicitud menciona contenido documental; requiere un archivo adjunto."
        ))
    if re.search(r"\b(imagen|foto|fotografía|captura|imagen adjunta)\b", texto):
        candidatas.append(HerramientaPlaneada(
            "vision", "La solicitud puede requerir una imagen adjunta y un proveedor de visión configurado."
        ))
    if re.search(r"\b(recuerda|recordar|memoria|te dije|habíamos hablado|antes te conté)\b", texto):
        candidatas.append(HerramientaPlaneada(
            "memory_retrieval", "La solicitud hace referencia a información personal previa."
        ))
    if re.search(r"\b(envía|envia|publica|compra|borra|elimina|modifica|reserva|contrata|sube a producción|despliega)\b", texto):
        candidatas.append(HerramientaPlaneada(
            "user_approved_action", "Se detectó una posible acción con efectos externos o irreversibles.",
            requiere_confirmacion=True,
        ))

    tarea, motivo = clasificar_tarea(mensaje)
    return {
        "task": tarea,
        "task_reason": motivo,
        "tools": [
            {"name": item.nombre, "reason": item.motivo,
             "requires_confirmation": item.requiere_confirmacion,
             "status": "planned_not_executed"}
            for item in candidatas
        ],
        "execution_policy": "No se ejecutan herramientas ni acciones externas desde este plan.",
    }
