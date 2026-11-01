"""Detección conservadora de posibles discrepancias entre textos de fuentes.

No determina qué fuente tiene razón. Solo señala pares que merecen revisión.
"""
from __future__ import annotations
import re
from itertools import combinations

_STOP = {
    'para','como','desde','hasta','sobre','entre','donde','cuando','porque','pero','tambien',
    'este','esta','estos','estas','ese','esa','unos','unas',' the ',' with ',' from ',' that ',
    'this','that','have','has','were','was','will','would','could','should','their','there',
    'que','del','las','los','una','uno','por','con','sin','sus','son','ser','fue','han','hay',
    'más','menos','segun','según','durante','tras','ante','cada','todo','toda','todos','todas'
}
_NEG = {'no','nunca','ningun','ninguna','ninguno','sin','false','not','never','neither'}
_NUM_RE = re.compile(r'(?<!\w)(?:\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)(?:\s?%|\s?(?:millones?|mil|km|kg|años?|year|years))?', re.I)
_TOKEN_RE = re.compile(r"[a-záéíóúüñ]{3,}", re.I)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|[\n•]+', text or '') if len(s.strip()) >= 35][:80]


def _features(sentence: str) -> dict:
    low = sentence.lower()
    tokens = {t for t in _TOKEN_RE.findall(low) if t not in _STOP}
    nums = {re.sub(r'\s+', '', n.lower()).replace(',', '.') for n in _NUM_RE.findall(low)}
    neg = any(re.search(r'\b' + re.escape(n) + r'\b', low) for n in _NEG)
    return {'tokens': tokens, 'numbers': nums, 'negative': neg}


def detectar_discrepancias(sources: list[dict], min_shared_terms: int = 4, max_candidates: int = 8) -> dict:
    docs = []
    for i, source in enumerate(sources[:5]):
        if source.get('page_read') is not True:
            continue
        text = str(source.get('page_text') or '')[:1800]
        for sentence in _sentences(text):
            f = _features(sentence)
            if len(f['tokens']) >= min_shared_terms:
                docs.append({'index': i, 'domain': str(source.get('domain') or ''),
                             'url': str(source.get('url') or '')[:2000],
                             'sentence': sentence[:500], **f})
    candidates = []
    for a, b in combinations(docs, 2):
        if a['index'] == b['index']:
            continue
        shared = a['tokens'] & b['tokens']
        if len(shared) < min_shared_terms:
            continue
        numeric_conflict = bool(a['numbers'] and b['numbers'] and a['numbers'].isdisjoint(b['numbers']))
        polarity_conflict = a['negative'] != b['negative']
        if not (numeric_conflict or polarity_conflict):
            continue
        candidates.append({
            'type': 'valores_distintos' if numeric_conflict else 'polaridad_distinta',
            'shared_terms': sorted(shared)[:12],
            'source_a': {'domain': a['domain'], 'url': a['url'], 'excerpt': a['sentence']},
            'source_b': {'domain': b['domain'], 'url': b['url'], 'excerpt': b['sentence']},
            'review_required': True,
            'warning': 'Posible discrepancia automática; puede deberse a fechas, población, unidades o contexto diferentes.'
        })
        if len(candidates) >= max_candidates:
            break
    return {
        'method': 'coincidencia_lexica_y_comparacion_de_numeros_o_polaridad',
        'candidates': candidates,
        'candidate_count': len(candidates),
        'sources_compared': len({d['index'] for d in docs}),
        'note': ('Se encontraron posibles discrepancias que requieren revisión contextual.' if candidates
                 else 'No se encontraron discrepancias con estas reglas; esto no demuestra que las fuentes coincidan.')
    }
