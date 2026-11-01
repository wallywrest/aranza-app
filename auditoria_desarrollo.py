"""Auditoría estática y de solo lectura para el proyecto Aranza.

No importa ni ejecuta módulos del proyecto, no instala paquetes, no invoca shell,
no modifica archivos y no envía código a servicios externos.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
from datetime import datetime, timezone

EXCLUDED = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build'}


def inspect_project(root: Path) -> dict:
    root = root.resolve()
    py_files = [p for p in root.rglob('*.py') if not any(part in EXCLUDED for part in p.parts)]
    test_files = [p for p in py_files if p.name.startswith('test_')]
    findings, modules, route_map = [], [], {}
    for path in sorted(py_files):
        rel = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=rel)
            compile(tree, rel, 'exec')
            status = 'ok'
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(('test_', 'TODO_')):
                    continue
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in {'get', 'post', 'put', 'patch', 'delete'} and decorator.args:
                                arg = decorator.args[0]
                                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    route_map.setdefault((decorator.func.attr.upper(), arg.value), []).append((rel, node.lineno, node.name))
            modules.append({'file': rel, 'status': status, 'lines': len(source.splitlines())})
        except (OSError, UnicodeError, SyntaxError, ValueError, TypeError) as exc:
            findings.append({'severity': 'error', 'file': rel, 'line': getattr(exc, 'lineno', None), 'message': str(exc)[:300]})
            modules.append({'file': rel, 'status': 'error', 'lines': None})
    for (method, route), owners in route_map.items():
        if len(owners) > 1:
            findings.append({'severity': 'review', 'file': owners[0][0], 'line': owners[0][1],
                             'message': f'Ruta potencialmente duplicada {method} {route}: ' + ', '.join(f'{f}:{ln} ({name})' for f, ln, name in owners)})
    for path in sorted(root.rglob('*')):
        if not path.is_file() or any(part in EXCLUDED for part in path.parts):
            continue
        if path.suffix.lower() not in {'.py', '.js', '.html', '.md'}:
            continue
        try:
            for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                upper = line.upper()
                if any(marker in upper for marker in ('TODO', 'FIXME', 'XXX')):
                    findings.append({'severity': 'info', 'file': path.relative_to(root).as_posix(),
                                     'line': number, 'message': line.strip()[:240]})
        except (OSError, UnicodeError):
            pass
    return {
        'tool': 'aranza_static_audit', 'read_only': True,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'python_files': len(py_files), 'test_files': len(test_files),
        'syntax_ok': sum(1 for m in modules if m['status'] == 'ok'),
        'syntax_errors': sum(1 for m in modules if m['status'] != 'ok'),
        'findings': findings, 'modules': modules,
        'limitations': ['No ejecuta pruebas ni importa módulos.', 'No demuestra corrección funcional ni seguridad completa.',
                        'Las rutas duplicadas y marcadores requieren revisión humana.']
    }


def render_markdown(report: dict) -> str:
    lines = ['# Auditoría estática de Aranza', '', f"- Archivos Python: {report['python_files']}",
             f"- Archivos de pruebas: {report['test_files']}", f"- Sintaxis correcta: {report['syntax_ok']}",
             f"- Errores de sintaxis: {report['syntax_errors']}", '', '## Hallazgos']
    if not report['findings']:
        lines.append('Sin hallazgos estáticos.')
    for item in report['findings']:
        lines.append(f"- **{item['severity']}** `{item['file']}:{item.get('line') or '-'}`: {item['message']}")
    lines += ['', '## Límites'] + [f'- {item}' for item in report['limitations']]
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Auditoría estática, local y de solo lectura de Aranza')
    parser.add_argument('project', nargs='?', default='.', help='Carpeta del proyecto')
    parser.add_argument('--json', dest='json_path', default='auditoria_aranza.json')
    parser.add_argument('--markdown', dest='md_path', default='auditoria_aranza.md')
    args = parser.parse_args()
    root = Path(args.project)
    if not root.is_dir():
        parser.error('La carpeta del proyecto no existe.')
    report = inspect_project(root)
    Path(args.json_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    Path(args.md_path).write_text(render_markdown(report), encoding='utf-8')
    print(f"Auditoría terminada: {report['syntax_ok']}/{report['python_files']} archivos Python con sintaxis válida; {len(report['findings'])} hallazgos.")
    return 1 if report['syntax_errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
