"""Pruebas para selección contextual de recuerdos."""
import main


def test_relevant_memories_ranked_first_and_limited():
    memories = [
        {"id": 3, "category": "general", "content": "Tengo un gato naranja"},
        {"id": 2, "category": "proyectos", "content": "Mi objetivo es aprender Excel para la universidad"},
        {"id": 1, "category": "preferencias", "content": "Prefiero respuestas directas y breves"},
    ]
    result = main.seleccionar_memorias_relevantes("Ayúdame con Excel para la universidad", memories, limite=2)
    assert 1 <= len(result) <= 2
    assert result[0]["content"] == "Mi objetivo es aprender Excel para la universidad"


def test_irrelevant_query_uses_small_fallback_not_every_memory():
    memories = [
        {"id": 5, "category": "general", "content": "Dato aleatorio uno"},
        {"id": 4, "category": "preferencias", "content": "Prefiero respuestas directas"},
        {"id": 3, "category": "proyectos", "content": "Mi proyecto es aprender Excel"},
        {"id": 2, "category": "general", "content": "Dato aleatorio dos"},
        {"id": 1, "category": "general", "content": "Dato aleatorio tres"},
    ]
    result = main.seleccionar_memorias_relevantes("¿Qué tiempo hace hoy?", memories, limite=8)
    assert len(result) <= 3
    assert all(item["category"] in ("preferencias", "proyectos") for item in result)


def test_memory_selection_handles_empty_inputs():
    assert main.seleccionar_memorias_relevantes("tema", [], limite=8) == []
    assert main.seleccionar_memorias_relevantes("tema", [{"category": "general", "content": "x"}], limite=0) == []


def test_strong_match_filters_weak_shared_topic_distractor():
    memories = [
        {"id": 1, "category": "proyectos", "content": "Presupuesto y costos del proyecto escolar"},
        {"id": 2, "category": "proyectos", "content": "Proyecto escolar: presentación de historia"},
    ]
    result = main.seleccionar_memorias_relevantes("presupuesto costos del proyecto", memories, limite=8)
    assert [item["id"] for item in result] == [1]


def test_weak_match_is_kept_when_no_strong_candidate_exists():
    memories = [
        {"id": 1, "category": "general", "content": "Prefiero explicaciones breves y directas"},
    ]
    result = main.seleccionar_memorias_relevantes("Excel universidad explicaciones", memories, limite=8)
    assert result == memories
