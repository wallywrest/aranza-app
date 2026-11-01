from datetime import date
from evaluacion_fuentes import evaluar_fuentes, _publication_date


def source(text, read=True, url='https://example.org/report'):
    return {'url': url, 'domain': 'example.org', 'snippet': 'fragmento',
            'page_read': read, 'page_text': text if read else ''}


def test_extracts_iso_date_and_calculates_freshness_signal():
    result = evaluar_fuentes([source('Publicado el 2026-10-01. ' + 'contenido ' * 80)],
                             as_of=date(2026, 10, 31))
    item = result['sources'][0]
    assert item['publication_date_candidate'] == '2026-10-01'
    assert item['age_days_candidate'] == 30
    assert item['freshness_signal'] == 'reciente_90_dias'


def test_extracts_spanish_long_date():
    assert _publication_date('Actualizado el 5 de octubre de 2025') == '2025-10-05'


def test_invalid_date_is_ignored():
    assert _publication_date('Fecha 2025-02-31') is None


def test_unread_search_snippet_is_not_assigned_publication_date():
    result = evaluar_fuentes([source('Publicado el 2026-10-01', read=False)], as_of=date(2026, 10, 31))
    item = result['sources'][0]
    assert item['publication_date_candidate'] is None
    assert item['context_available'] == 'solo_fragmento'


def test_evidence_matrix_has_stable_source_ids_and_limits():
    result = evaluar_fuentes([source('Publicado el 2026-01-01. ' + 'texto ' * 100), source('texto', url='https://other.net/a')], as_of=date(2026, 10, 31))
    assert [x['source_id'] for x in result['evidence_matrix']] == ['S1', 'S2']
    assert result['evidence_matrix'][1]['freshness_signal'] == 'fecha_no_identificada'
    assert result['assessment_limits']


def test_date_candidate_is_explicitly_unverified():
    result = evaluar_fuentes([source('Publicado el 2026-10-01. ' + 'contenido ' * 80)], as_of=date(2026, 10, 31))
    assert any('candidata' in x for x in result['sources'][0]['limitations'])
