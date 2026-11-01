from evaluacion_fuentes import evaluar_fuentes


def test_no_confunde_https_con_veracidad():
    result = evaluar_fuentes([{'url':'https://example.com/a','domain':'example.com','page_read':True,'page_text':'x'*600}])
    source = result['sources'][0]
    assert source['evidence_level'] == 'lectura_con_mas_contexto'
    assert any('HTTPS' in item for item in source['signals'])
    assert any('no prueban veracidad' in item for item in source['limitations'])


def test_distingue_fragmento_de_pagina_leida():
    result = evaluar_fuentes([{'url':'https://example.org','domain':'example.org','snippet':'texto','page_read':False}])
    assert result['sources'][0]['evidence_level'] == 'fragmento_no_verificado'
    assert result['warnings']


def test_dominios_institucionales_solo_son_senales():
    result = evaluar_fuentes([{'url':'https://sitio.gob.mx','domain':'sitio.gob.mx','page_read':True,'page_text':'dato'}])
    assert any('no garantiza' in item for item in result['sources'][0]['signals'])
    assert result['contradiction_candidates'] == []
    assert 'No se encontraron discrepancias' in result['contradiction_note']


def test_limita_a_cinco_fuentes():
    result = evaluar_fuentes([{'url':f'https://a{i}.com','page_read':False} for i in range(8)])
    assert len(result['sources']) == 5
