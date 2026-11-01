from pathlib import Path
from auditoria_desarrollo import inspect_project, render_markdown


def test_audit_is_read_only_and_reports_python_syntax(tmp_path):
    (tmp_path / 'main.py').write_text('def hello():\n    return "ok"\n', encoding='utf-8')
    (tmp_path / 'test_main.py').write_text('def test_ok():\n    assert True\n', encoding='utf-8')
    before = sorted(p.name for p in tmp_path.iterdir())
    report = inspect_project(tmp_path)
    after = sorted(p.name for p in tmp_path.iterdir())
    assert report['read_only'] is True
    assert report['python_files'] == 2
    assert report['test_files'] == 1
    assert report['syntax_errors'] == 0
    assert before == after


def test_audit_reports_syntax_error_and_duplicate_routes(tmp_path):
    (tmp_path / 'broken.py').write_text('def broken(:\n pass\n', encoding='utf-8')
    (tmp_path / 'api.py').write_text('''\n@app.get("/same")\ndef first(): pass\n@app.get("/same")\ndef second(): pass\n''', encoding='utf-8')
    report = inspect_project(tmp_path)
    assert report['syntax_errors'] == 1
    assert any('Ruta potencialmente duplicada' in x['message'] for x in report['findings'])
    assert 'No ejecuta pruebas' in render_markdown(report)


def test_audit_ignores_virtualenv_and_cache(tmp_path):
    (tmp_path / '.venv').mkdir()
    (tmp_path / '.venv' / 'ignored.py').write_text('def broken(:', encoding='utf-8')
    (tmp_path / 'ok.py').write_text('VALUE = 1', encoding='utf-8')
    report = inspect_project(tmp_path)
    assert report['python_files'] == 1
    assert report['syntax_errors'] == 0
