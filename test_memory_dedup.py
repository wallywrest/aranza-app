"""Pruebas para evitar recuerdos redundantes en el contexto."""
import main


def test_context_selection_removes_exact_duplicate_memories():
    memories = [
        {"id": 1, "category": "proyectos", "content": "Estoy aprendiendo Excel para la universidad"},
        {"id": 2, "category": "proyectos", "content": "Estoy aprendiendo Excel para la universidad"},
        {"id": 3, "category": "general", "content": "Uso Excel en la universidad"},
    ]
    result = main.seleccionar_memorias_relevantes("Excel universidad", memories, limite=8)
    assert sum(m["content"] == "Estoy aprendiendo Excel para la universidad" for m in result) == 1


def test_context_selection_removes_near_duplicates_but_keeps_distinct_memories():
    memories = [
        {"id": 1, "category": "proyectos", "content": "Mi objetivo es aprender Excel para la universidad"},
        {"id": 2, "category": "proyectos", "content": "Mi objetivo es aprender Excel para la universidad ahora"},
        {"id": 3, "category": "preferencias", "content": "Prefiero explicaciones breves y directas"},
    ]
    result = main.seleccionar_memorias_relevantes("Excel universidad explicaciones", memories, limite=8)
    contents = [m["content"] for m in result]
    assert len(contents) == len(set(contents))
    assert any("explicaciones" in content for content in contents)


def test_archived_memories_stay_excluded_after_deduplication():
    memories = [
        {"id": 1, "category": "proyectos", "content": "Aprendo Excel", "status": "archived"},
        {"id": 2, "category": "proyectos", "content": "Aprendo Excel", "status": "active"},
    ]
    result = main.seleccionar_memorias_relevantes("Excel", memories, limite=8)
    assert result == [memories[1]]
