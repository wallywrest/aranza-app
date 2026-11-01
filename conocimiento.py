"""Búsqueda local explicable para la biblioteca privada de Aranza.

No es búsqueda semántica neuronal: usa coincidencia léxica ponderada,
normalización y cobertura de términos, sin enviar datos a terceros.
"""
from __future__ import annotations
import re
import unicodedata
from collections import Counter

_STOPWORDS = {
    "a", "al", "algo", "algunos", "ante", "como", "con", "contra", "cual",
    "cuando", "de", "del", "desde", "donde", "dos", "el", "ella", "en",
    "entre", "era", "es", "esa", "ese", "eso", "esta", "este", "esto",
    "fue", "ha", "hasta", "hay", "la", "las", "lo", "los", "mas", "me",
    "mi", "mis", "muy", "no", "o", "para", "pero", "por", "que", "se",
    "sin", "sobre", "su", "sus", "un", "una", "uno", "unos", "y", "ya",
}


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def tokenize(value: object) -> list[str]:
    return [t for t in normalize_text(value).split() if len(t) > 1 and t not in _STOPWORDS]


def rank_research(query: str, rows: list[dict], limit: int = 20) -> list[dict]:
    """Rankea expedientes por coincidencia ponderada y cobertura de consulta."""
    terms = list(dict.fromkeys(tokenize(query)))
    if not terms:
        return []
    docs = []
    document_frequency = Counter()
    for row in rows:
        sources = row.get("sources", [])
        source_text = " ".join(
            f"{s.get('title', '')} {s.get('domain', '')} {s.get('snippet', '')}"
            for s in sources if isinstance(s, dict)
        )
        fields = {
            "title": tokenize(row.get("title")),
            "query": tokenize(row.get("query")),
            "summary": tokenize(row.get("summary")),
            "tags": tokenize(" ".join(row.get("tags", []))),
            "sources": tokenize(source_text),
        }
        present = set().union(*(set(v) for v in fields.values()))
        document_frequency.update(present)
        docs.append((row, fields, present))
    total = max(1, len(docs))
    ranked = []
    normalized_query = normalize_text(query)
    for row, fields, present in docs:
        score = 0.0
        matched = []
        field_weights = {"title": 5.0, "query": 4.0, "tags": 3.5, "summary": 2.0, "sources": 1.0}
        for term in terms:
            if term not in present:
                continue
            matched.append(term)
            idf = 1.0 + (total / (1 + document_frequency[term])) ** 0.35
            for field, tokens in fields.items():
                if term in tokens:
                    score += field_weights[field] * idf * (1.0 + 0.12 * (tokens.count(term) - 1))
        coverage = len(matched) / len(terms)
        if coverage < 0.25:
            continue
        score *= 0.65 + 0.35 * coverage
        if normalized_query and normalized_query in normalize_text(row.get("title")):
            score += 8.0
        ranked.append({
            "id": row["id"], "title": row.get("title", ""),
            "query": row.get("query", ""), "summary": row.get("summary", "")[:360],
            "tags": row.get("tags", []), "source_count": row.get("source_count", 0),
            "created_at": row.get("created_at"), "updated_at": row.get("updated_at"),
            "score": round(score, 3), "coverage": round(coverage, 3),
            "matched_terms": matched,
        })
    ranked.sort(key=lambda item: (item["score"], item.get("updated_at") or ""), reverse=True)
    return ranked[:max(1, min(int(limit), 50))]
