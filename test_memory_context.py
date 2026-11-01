"""Pruebas para la construcción de contexto de memoria v1.24."""
import main


def test_memory_query_prioritizes_current_message_and_adds_recent_user_context():
    history = [
        {"role": "user", "content": "Estoy aprendiendo Excel"},
        {"role": "assistant", "content": "Vamos paso a paso"},
        {"role": "user", "content": "Quiero organizar mi horario de estudio"},
    ]
    query = main.construir_consulta_memoria("Ayúdame con mi proyecto", history)
    assert query.startswith("Ayúdame con mi proyecto Ayúdame con mi proyecto")
    assert "Estoy aprendiendo Excel" in query
    assert "Quiero organizar mi horario de estudio" in query
    assert "Vamos paso a paso" not in query


def test_memory_relevance_ignores_accents_and_matches_common_spanish_forms():
    memories = [
        {"category": "general", "content": "Estoy estudiando ingeniería y administración"},
        {"category": "general", "content": "Me gusta la jardinería"},
    ]
    result = main.seleccionar_memorias_relevantes("estudio ingenieria", memories)
    assert result
    assert result[0]["content"] == "Estoy estudiando ingeniería y administración"


def test_memory_query_handles_missing_history():
    assert main.construir_consulta_memoria("Hola", None) == "Hola Hola"
