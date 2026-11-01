from comparador_afirmaciones import detectar_discrepancias


def test_detecta_cifras_distintas_con_contexto_lexico_compartido():
    sources = [
        {'domain': 'a.example', 'url': 'https://a.example', 'page_read': True,
         'page_text': 'La población total registrada en el municipio durante el año fue de 1200 habitantes.'},
        {'domain': 'b.example', 'url': 'https://b.example', 'page_read': True,
         'page_text': 'La población total registrada en el municipio durante el año fue de 1500 habitantes.'},
    ]
    result = detectar_discrepancias(sources)
    assert result['candidate_count'] == 1
    assert result['candidates'][0]['type'] == 'valores_distintos'
    assert result['candidates'][0]['review_required'] is True


def test_no_compara_fragmentos_no_leidos():
    sources = [
        {'domain': 'a.example', 'page_read': False, 'snippet': 'dato 100'},
        {'domain': 'b.example', 'page_read': False, 'snippet': 'dato 200'},
    ]
    result = detectar_discrepancias(sources)
    assert result['candidate_count'] == 0
    assert result['sources_compared'] == 0


def test_no_llama_contradiccion_a_cifras_sin_contexto_comun():
    sources = [
        {'domain': 'a.example', 'page_read': True, 'page_text': 'La temperatura media anual registrada en la región norte alcanzó 20 grados.'},
        {'domain': 'b.example', 'page_read': True, 'page_text': 'El presupuesto total aprobado para educación alcanzó 30 millones.'},
    ]
    assert detectar_discrepancias(sources)['candidate_count'] == 0


def test_evaluacion_integra_comparacion():
    from evaluacion_fuentes import evaluar_fuentes
    result = evaluar_fuentes([
        {'url': 'https://a.example', 'domain': 'a.example', 'page_read': True,
         'page_text': 'La población total registrada en el municipio durante el año fue de 1200 habitantes.'},
        {'url': 'https://b.example', 'domain': 'b.example', 'page_read': True,
         'page_text': 'La población total registrada en el municipio durante el año fue de 1500 habitantes.'},
    ])
    assert 'claim_comparison' in result
    assert len(result['contradiction_candidates']) == 1
