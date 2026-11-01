"""Clasifica y resume informes de auditoría estática de Aranza.

Consume JSON generado por auditoria_desarrollo.py. No abre ni modifica
archivos del proyecto auditado, no ejecuta código y no aplica correcciones.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SEVERITY_ORDER = {'error': 0, 'review': 1, 'info': 2}
CATEGORY_RULES = (
    ('sintaxis', ('syntaxerror', 'invalid syntax', 'unexpected eof', 'was never closed')),
    ('rutas_api', ('ruta potencialmente duplicada', 'duplicate route')),
    ('pendientes', ('todo', 'fixme', 'xxx')),
)


def _category(message: str, severity: str) -> str:
    normalized = message.casefold()
    for category, needles in CATEGORY_RULES:
        if any(needle in normalized for needle in needles):
            return category
    return 'otros' if severity != 'info' else 'informativo'


def analyze_report(report: dict) -> dict:
    if not isinstance(report, dict) or not isinstance(report.get('findings'), list):
        raise ValueError('El JSON no tiene la estructura de un informe de auditoría válido.')
    if report.get('tool') not in (None, 'aranza_static_audit'):
        raise ValueError('El informe pertenece a una herramienta no reconocida.')
    unique = {}
    for raw in report['findings']:
        if not isinstance(raw, dict):
            continue
        severity = str(raw.get('severity', 'info')).lower()
        if severity not in SEVERITY_ORDER:
            severity = 'info'
        file = str(raw.get('file') or '(archivo desconocido)')[:300]
        line = raw.get('line')
        if not isinstance(line, int) or line < 1:
            line = None
        message = ' '.join(str(raw.get('message') or 'Hallazgo sin descripción').split())[:500]
        fingerprint = hashlib.sha256(f'{severity}|{file}|{line}|{message.casefold()}'.encode()).hexdigest()[:16]
        unique.setdefault(fingerprint, {
            'id': fingerprint, 'severity': severity, 'category': _category(message, severity),
            'file': file, 'line': line, 'message': message,
            'action': _action(severity, _category(message, severity)),
        })
    findings = sorted(unique.values(), key=lambda x: (SEVERITY_ORDER[x['severity']], x['file'], x['line'] or 0, x['id']))
    counts = Counter(x['severity'] for x in findings)
    categories = Counter(x['category'] for x in findings)
    return {
        'tool': 'aranza_audit_review', 'source_tool': report.get('tool', 'unknown'),
        'source_generated_at': report.get('generated_at'), 'read_only': True,
        'automatic_fixes_applied': 0, 'total_received': len(report['findings']),
        'total_unique': len(findings), 'duplicates_removed': len(report['findings']) - len(findings),
        'severity_counts': {key: counts.get(key, 0) for key in ('error', 'review', 'info')},
        'category_counts': dict(sorted(categories.items())), 'findings': findings,
        'limitations': [
            'La clasificación es heurística y puede equivocarse.',
            'Un hallazgo informativo no demuestra que exista un defecto.',
            'No se inspecciona el código fuente ni se verifica si el hallazgo sigue vigente.',
            'No se modifica el proyecto ni se aplican correcciones automáticamente.',
        ],
    }


def _action(severity: str, category: str) -> str:
    if category == 'sintaxis' or severity == 'error':
        return 'Revisar primero el archivo y la línea; confirmar el error antes de editar.'
    if category == 'rutas_api':
        return 'Comprobar si ambas rutas se registran en la misma aplicación y si la coincidencia es intencional.'
    if category == 'pendientes':
        return 'Determinar si el marcador sigue vigente o aparece solo en documentación o ejemplos.'
    return 'Inspeccionar el contexto y decidir manualmente si requiere una acción.'


def render_markdown(result: dict) -> str:
    counts = result['severity_counts']
    lines = ['# Revisión del informe de auditoría', '',
             f"- Hallazgos recibidos: {result['total_received']}",
             f"- Hallazgos únicos: {result['total_unique']}",
             f"- Duplicados agrupados: {result['duplicates_removed']}",
             f"- Errores: {counts['error']} | Revisión: {counts['review']} | Informativos: {counts['info']}",
             '- Cambios automáticos aplicados: 0', '', '## Hallazgos priorizados']
    if not result['findings']:
        lines.append('No hay hallazgos en el informe de entrada.')
    for item in result['findings']:
        location = f"{item['file']}:{item['line'] or '-'}"
        lines += [f"### {item['severity'].upper()} · {item['category']}",
                  f"- Ubicación: `{location}`", f"- Descripción: {item['message']}",
                  f"- Siguiente revisión: {item['action']}", '']
    lines += ['## Límites'] + [f'- {x}' for x in result['limitations']]
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Resume y prioriza un JSON de auditoría sin modificar el proyecto.')
    parser.add_argument('input', help='Informe JSON generado por auditoria_desarrollo.py')
    parser.add_argument('--json', default='revision_auditoria.json', help='Ruta del resumen JSON')
    parser.add_argument('--markdown', default='revision_auditoria.md', help='Ruta del informe Markdown')
    args = parser.parse_args()
    try:
        report = json.loads(Path(args.input).read_text(encoding='utf-8'))
        result = analyze_report(report)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(f'No se pudo analizar el informe: {exc}')
    Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    Path(args.markdown).write_text(render_markdown(result), encoding='utf-8')
    print(f"Revisión lista: {result['total_unique']} hallazgos únicos; 0 cambios aplicados.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
