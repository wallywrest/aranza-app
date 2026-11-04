"""Pruebas aisladas para la selección de recuerdos de Aranza."""
import main


def test_seleccion_memoria_con_limite_cero_devuelve_lista_vacia():
    memorias = [{"id": 1, "category": "preferencias", "content": "Prefiero respuestas breves"}]
    assert main.seleccionar_memorias_relevantes("tema sin relación", memorias, limite=0) == []


def test_memorias_archivadas_no_entran_al_contexto():
    memorias = [
        {"id": 1, "category": "proyectos", "content": "Proyecto antiguo de ingeniería", "status": "archived"},
        {"id": 2, "category": "preferencias", "content": "Prefiero explicaciones claras", "status": "active"},
    ]
    resultado = main.seleccionar_memorias_relevantes("ingeniería y proyecto", memorias)
    assert all(item["id"] != 1 for item in resultado)


def test_memorias_duplicadas_no_se_repite_contexto():
    memorias = [
        {"id": 1, "category": "preferencias", "content": "Prefiero respuestas claras y breves"},
        {"id": 2, "category": "preferencias", "content": "Prefiero respuestas claras y breves"},
    ]
    resultado = main.seleccionar_memorias_relevantes("prefiero respuestas claras", memorias)
    assert len(resultado) == 1
