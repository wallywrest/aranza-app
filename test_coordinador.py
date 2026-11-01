import os

from coordinador import clasificar_tarea
from modelos import ProveedorModelo, proveedores_para_tarea


def test_clasifica_matematicas():
    assert clasificar_tarea("Calcula el 15% de 800") [0] == "math"


def test_clasifica_programacion():
    assert clasificar_tarea("Depura este error de Python") [0] == "coding"


def test_clasifica_analisis():
    assert clasificar_tarea("Analiza las causas y consecuencias") [0] == "analysis"


def test_clasifica_redaccion():
    assert clasificar_tarea("Redacta un correo formal") [0] == "writing"


def test_clasificacion_general():
    assert clasificar_tarea("Hola Aranza") [0] == "conversation"


def test_tarea_sin_modelo_especializado_usa_cadena_general(monkeypatch):
    monkeypatch.setattr("modelos.proveedores_configurados", lambda: [
        ProveedorModelo("general", "https://general.example/v1", "key", "model")
    ])
    for key in ("ARANZA_ANALYSIS_BASE_URL", "ARANZA_ANALYSIS_API_KEY", "ARANZA_ANALYSIS_MODEL"):
        monkeypatch.delenv(key, raising=False)
    result = proveedores_para_tarea("analysis")
    assert [p.nombre for p in result] == ["general"]


def test_tarea_especializada_precede_a_respaldo(monkeypatch):
    monkeypatch.setattr("modelos.proveedores_configurados", lambda: [
        ProveedorModelo("general", "https://general.example/v1", "key", "model")
    ])
    monkeypatch.setenv("ARANZA_ANALYSIS_BASE_URL", "https://special.example/v1")
    monkeypatch.setenv("ARANZA_ANALYSIS_API_KEY", "special-key")
    monkeypatch.setenv("ARANZA_ANALYSIS_MODEL", "analysis-model")
    result = proveedores_para_tarea("analysis")
    assert [p.nombre for p in result] == ["analysis-specialist", "general"]
    assert result[0].modelo == "analysis-model"


def test_planifica_busqueda_sin_ejecutarla():
    from coordinador import planificar_herramientas
    plan = planificar_herramientas("Busca noticias recientes sobre energía solar")
    assert plan["tools"][0]["name"] == "web_search"
    assert plan["tools"][0]["status"] == "planned_not_executed"
    assert "No se ejecutan" in plan["execution_policy"]


def test_planifica_documento_y_vision():
    from coordinador import planificar_herramientas
    plan = planificar_herramientas("Analiza este PDF y esta imagen")
    names = {item["name"] for item in plan["tools"]}
    assert {"file_analysis", "vision"}.issubset(names)


def test_accion_externa_exige_confirmacion():
    from coordinador import planificar_herramientas
    plan = planificar_herramientas("Envía este correo y elimina el borrador")
    accion = next(item for item in plan["tools"] if item["name"] == "user_approved_action")
    assert accion["requires_confirmation"] is True
    assert accion["status"] == "planned_not_executed"


def test_plan_general_no_inventa_herramientas():
    from coordinador import planificar_herramientas
    plan = planificar_herramientas("Hola Aranza")
    assert plan["tools"] == []


def test_planifica_investigacion_con_lectura_de_fuentes():
    from coordinador import planificar_herramientas
    plan = planificar_herramientas("Investiga fuentes sobre energía solar")
    assert plan["tools"][0]["name"] == "web_research"
    assert plan["tools"][0]["status"] == "planned_not_executed"
