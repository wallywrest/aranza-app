"""Evaluación prudente de evidencia web: señales, no veredictos de verdad."""
from __future__ import annotations
from urllib.parse import urlparse
from datetime import date, datetime
import re
from comparador_afirmaciones import detectar_discrepancias


_DATE_PATTERNS = [
    re.compile(r"\b(20\d{2})[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b"),
    re.compile(r"\b(0?[1-9]|[12]\d|3[01])\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\s+de\s+(20\d{2})\b", re.I),
]
_MONTHS = {'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'setiembre':9,'octubre':10,'noviembre':11,'diciembre':12}


def _publication_date(text: str):
    for pattern in _DATE_PATTERNS:
        match = pattern.search(text[:1800])
        if not match:
            continue
        try:
            if pattern is _DATE_PATTERNS[0]:
                return date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
            return date(int(match.group(3)), _MONTHS[match.group(2).lower()], int(match.group(1))).isoformat()
        except ValueError:
            continue
    return None


def evaluar_fuentes(sources: list[dict], as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    assessed = []
    for item in sources[:5]:
        url = str(item.get('url', ''))[:2000]
        parsed = urlparse(url)
        domain = (str(item.get('domain') or parsed.hostname or '').lower().strip('.'))[:253]
        read = item.get('page_read') is True
        text = str(item.get('page_text') or '')
        snippet = str(item.get('snippet') or '')
        signals = []
        publication_date = _publication_date(text) if read else None
        age_days = None
        freshness = 'fecha_no_identificada'
        if publication_date:
            age_days = max(0, (as_of - date.fromisoformat(publication_date)).days)
            freshness = 'reciente_90_dias' if age_days <= 90 else ('90_a_365_dias' if age_days <= 365 else 'mas_de_un_ano')
        if parsed.scheme == 'https': signals.append('Conexión HTTPS indicada en el enlace')
        else: signals.append('El enlace no acredita HTTPS')
        if read and len(text) >= 500: signals.append('Se pudo leer una parte sustancial de la página')
        elif read: signals.append('Se leyó solo un fragmento limitado de la página')
        else: signals.append('Solo hay un fragmento del buscador; página no verificada')
        if domain.endswith(('.gov', '.gob.mx', '.edu', '.edu.mx', '.int')):
            signals.append('Dominio institucional por sufijo; no garantiza que el contenido sea correcto')
        elif domain.endswith(('.com', '.org', '.net')):
            signals.append('Dominio genérico; la autoridad debe comprobarse por separado')
        evidence = 'lectura_parcial' if read else 'fragmento_no_verificado'
        if read and len(text) >= 500: evidence = 'lectura_con_mas_contexto'
        if publication_date:
            signals.append(f'Fecha encontrada en el texto: {publication_date} (señal automática, no metadato verificado)')
        else:
            signals.append('No se identificó una fecha de publicación en el texto disponible')
        assessed.append({
            'source_id': f'S{len(assessed)+1}',
            'url': url, 'domain': domain, 'evidence_level': evidence,
            'publication_date_candidate': publication_date, 'age_days_candidate': age_days,
            'freshness_signal': freshness,
            'context_available': 'pagina_leida' if read else 'solo_fragmento',
            'page_read': read, 'text_length': len(text), 'signals': signals,
            'limitations': ['No se verificó autoría, metodología ni revisión editorial.',
                            'La fecha, si aparece, es una candidata extraída del texto y puede ser incorrecta.',
                            'HTTPS y el tipo de dominio no prueban veracidad.']
        })
    domains = [x['domain'] for x in assessed if x['domain']]
    unique = len(set(domains))
    warnings = []
    if assessed and unique < min(2, len(assessed)):
        warnings.append('Las fuentes disponibles no ofrecen diversidad clara de dominios.')
    if any(not x['page_read'] for x in assessed):
        warnings.append('Al menos una fuente se basa únicamente en el fragmento del buscador.')
    comparison = detectar_discrepancias(sources)
    return {
        'method': 'heuristicas_de_evidencia_no_verificacion_de_verdad',
        'sources': assessed,
        'evidence_matrix': [{'source_id': x['source_id'], 'domain': x['domain'],
                             'evidence_level': x['evidence_level'],
                             'freshness_signal': x['freshness_signal'],
                             'publication_date_candidate': x['publication_date_candidate'],
                             'context_available': x['context_available']} for x in assessed],
        'assessment_limits': ['No hay puntuación global de verdad ni ranking automático de credibilidad.',
                              'La fecha se infiere del texto visible y requiere confirmación.',
                              'La evaluación no sustituye la lectura crítica de la fuente.'],
        'unique_domains': unique,
        'warnings': warnings,
        'contradiction_candidates': comparison['candidates'],
        'claim_comparison': comparison,
        'contradiction_note': comparison['note']
    }
