import json
import pytest
from informe_auditoria import analyze_report, render_markdown


def test_deduplicates_and_prioritizes_findings():
    report = {'tool': 'aranza_static_audit', 'findings': [
        {'severity': 'info', 'file': 'README.md', 'line': 2, 'message': 'TODO revisar'},
        {'severity': 'error', 'file': 'main.py', 'line': 8, 'message': 'SyntaxError: invalid syntax'},
        {'severity': 'error', 'file': 'main.py', 'line': 8, 'message': 'SyntaxError: invalid syntax'},
    ]}
    result = analyze_report(report)
    assert result['total_received'] == 3
    assert result['total_unique'] == 2
    assert result['duplicates_removed'] == 1
    assert result['findings'][0]['severity'] == 'error'
    assert result['automatic_fixes_applied'] == 0
    assert '0 cambios aplicados' in render_markdown(result) or 'Cambios automáticos aplicados: 0' in render_markdown(result)


def test_classifies_duplicate_route_and_unknown_severity():
    result = analyze_report({'findings': [
        {'severity': 'review', 'file': 'api.py', 'message': 'Ruta potencialmente duplicada GET /x'},
        {'severity': 'critical', 'file': 'x.py', 'message': 'Otra observación'},
    ]})
    assert result['findings'][0]['category'] == 'rutas_api'
    assert any(x['severity'] == 'info' for x in result['findings'])


def test_rejects_invalid_report_shape():
    with pytest.raises(ValueError):
        analyze_report({'findings': 'not-a-list'})


def test_empty_report_is_valid():
    result = analyze_report({'tool': 'aranza_static_audit', 'findings': []})
    assert result['total_unique'] == 0
    assert result['severity_counts'] == {'error': 0, 'review': 0, 'info': 0}
