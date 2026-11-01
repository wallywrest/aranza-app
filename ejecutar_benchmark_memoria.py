#!/usr/bin/env python3
"""Ejecuta un benchmark supervisado de recuperación de memoria en una BD temporal.

No toca la base de datos habitual de Aranza ni llama a proveedores externos.
El archivo de entrada opcional debe contener {"cases": [{name, query,
relevant, irrelevant?, category?, limit?}, ...]}. Las etiquetas relevantes son
referencias de prueba explícitas, no una verdad semántica universal.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


DEFAULT_CASES: list[dict[str, Any]] = [
    {
        "name": "direct_keyword_match",
        "query": "practicar inglés conversación",
        "relevant": ["estudiar inglés y practicar conversación"],
        "irrelevant": ["receta sopa verduras"],
        "category": "estudio",
        "group": "direct_match",
        "limit": 8,
    },
    {
        "name": "accent_normalization",
        "query": "alimentación saludable",
        "relevant": ["consejos de alimentacion saludable"],
        "irrelevant": ["mantenimiento de bicicleta"],
        "category": "bienestar",
        "group": "normalization",
        "limit": 8,
    },
    {
        "name": "project_relevance",
        "query": "proyecto construir aplicación",
        "relevant": ["objetivo del proyecto construir aplicación web"],
        "irrelevant": ["historia del arte antiguo"],
        "category": "proyecto",
        "group": "project_context",
        "limit": 8,
    },
    {
        "name": "archived_memory_excluded",
        "query": "astronomía telescopio planetas",
        "relevant": ["astronomía telescopio planetas"],
        "irrelevant": [],
        "category": "estudio",
        "group": "archived_memory",
        "limit": 8,
        "archive_relevant": True,
    },
    {
        "name": "multiple_relevant_memories",
        "query": "plan de inglés conversación vocabulario",
        "relevant": ["practicar conversación en inglés", "aprender vocabulario en inglés"],
        "irrelevant": ["reparar bicicleta urbana"],
        "category": "estudio",
        "group": "multi_memory",
        "limit": 8,
    },
    {
        "name": "near_topic_distractor",
        "query": "presupuesto del proyecto",
        "relevant": ["presupuesto y costos del proyecto escolar"],
        "irrelevant": ["proyecto escolar: presentación de historia"],
        "category": "proyecto",
        "group": "distractors",
        "limit": 8,
    },
]


class ScenarioError(ValueError):
    pass


def _validate_cases(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list) or not raw["cases"]:
        raise ScenarioError("El archivo debe contener una lista no vacía 'cases'.")
    seen: set[str] = set()
    cases: list[dict[str, Any]] = []
    for i, item in enumerate(raw["cases"]):
        if not isinstance(item, dict):
            raise ScenarioError(f"cases[{i}] debe ser un objeto.")
        name = item.get("name")
        query = item.get("query")
        relevant = item.get("relevant")
        irrelevant = item.get("irrelevant", [])
        if not isinstance(name, str) or not name.strip():
            raise ScenarioError(f"cases[{i}].name debe ser texto no vacío.")
        name = name.strip()
        if name in seen:
            raise ScenarioError(f"Nombre de escenario duplicado: {name!r}.")
        seen.add(name)
        if not isinstance(query, str) or not query.strip() or len(query) > 4000:
            raise ScenarioError(f"{name}.query debe tener entre 1 y 4000 caracteres.")
        if not isinstance(relevant, list) or not relevant or any(not isinstance(x, str) or not x.strip() for x in relevant):
            raise ScenarioError(f"{name}.relevant debe ser una lista no vacía de textos.")
        if not isinstance(irrelevant, list) or any(not isinstance(x, str) or not x.strip() for x in irrelevant):
            raise ScenarioError(f"{name}.irrelevant debe ser una lista de textos no vacíos.")
        limit = item.get("limit", 8)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
            raise ScenarioError(f"{name}.limit debe ser un entero entre 1 y 20.")
        category = item.get("category", "general")
        if not isinstance(category, str) or not category.strip():
            raise ScenarioError(f"{name}.category debe ser texto no vacío.")
        group = item.get("group", "general")
        if not isinstance(group, str) or not group.strip() or len(group) > 80:
            raise ScenarioError(f"{name}.group debe ser texto no vacío de hasta 80 caracteres.")
        archive_relevant = item.get("archive_relevant", False)
        if not isinstance(archive_relevant, bool):
            raise ScenarioError(f"{name}.archive_relevant debe ser booleano.")
        cases.append({
            "name": name, "query": query.strip(), "relevant": [x.strip() for x in relevant],
            "irrelevant": [x.strip() for x in irrelevant], "category": category.strip(),
            "group": group.strip(), "limit": limit, "archive_relevant": archive_relevant,
        })
    return cases


def _fingerprint(case: dict[str, Any]) -> str:
    canonical = json.dumps(case, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _token(account_id: str, main_module: Any) -> dict[str, str]:
    expires_at = int(time.time()) + main_module.SESSION_TTL_SECONDS
    nonce = f"benchmark-{account_id}-{time.time_ns()}"
    with main_module.conectar_db() as conn:
        conn.execute(
            "INSERT INTO sesiones(nonce, account_id, expires_at) VALUES (?, ?, ?)",
            (nonce, account_id, expires_at),
        )
    payload = json.dumps(
        {"exp": expires_at, "nonce": nonce, "account_id": account_id}, separators=(",", ":")
    ).encode("utf-8")
    body = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(
        hmac.new(main_module._session_secret(), body.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    return {"Authorization": f"Bearer {body}.{signature}"}


def run(cases: list[dict[str, Any]]) -> dict[str, Any]:
    # Set the DB path before importing main so all writes stay inside a disposable sandbox.
    with tempfile.TemporaryDirectory(prefix="aranza-benchmark-") as temp_dir:
        os.environ["ARANZA_DB_PATH"] = str(Path(temp_dir) / "benchmark.sqlite3")
        os.environ.setdefault("ARANZA_SESSION_SECRET", "local-benchmark-secret-not-for-production")
        import main  # noqa: PLC0415
        from fastapi.testclient import TestClient  # noqa: PLC0415

        output_cases = []
        with TestClient(main.app) as client:
            for index, case in enumerate(cases):
                account = f"benchmark-{index}-{time.time_ns()}"
                expected_ids = []
                for content in case["relevant"]:
                    expected_ids.append(main.guardar_memoria(content, case["category"], account_id=account))
                for content in case["irrelevant"]:
                    main.guardar_memoria(content, "benchmark_irrelevant", account_id=account)
                if case["archive_relevant"]:
                    with main.conectar_db() as conn:
                        conn.executemany(
                            "UPDATE memorias SET status='archived' WHERE id=? AND account_id=?",
                            [(memory_id, account) for memory_id in expected_ids],
                        )
                response = client.post(
                    "/memory/context-evaluate", headers=_token(account, main),
                    json={"query": case["query"], "expected_memory_ids": expected_ids, "limit": case["limit"]},
                )
                if response.status_code != 200:
                    raise RuntimeError(f"Escenario {case['name']!r}: API devolvió {response.status_code}: {response.text}")
                result = response.json()
                output_cases.append({
                    "name": case["name"], "group": case["group"], "fingerprint": _fingerprint(case),
                    "precision": result["precision"], "recall": result["recall"], "f1": result["f1"],
                    "expected_count": result["expected_count"], "retrieved_count": result["retrieved_count"],
                    "missed_expected_count": len(result["missed_expected_ids"]),
                    "unexpected_retrieved_count": len(result["unexpected_retrieved_ids"]),
                    "model_called": result["model_called"], "history_saved": result["history_saved"],
                    "automatic_changes": result["automatic_changes"],
                })
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in output_cases:
            grouped.setdefault(item["group"], []).append(item)
        group_summary = {
            group: {
                "case_count": len(items),
                "precision_macro_avg": round(sum(x["precision"] for x in items) / len(items), 4),
                "recall_macro_avg": round(sum(x["recall"] for x in items) / len(items), 4),
                "f1_macro_avg": round(sum(x["f1"] for x in items) / len(items), 4),
                "missed_expected_total": sum(x["missed_expected_count"] for x in items),
                "unexpected_retrieved_total": sum(x["unexpected_retrieved_count"] for x in items),
            }
            for group, items in sorted(grouped.items())
        }
        return {
            "schema_version": 1,
            "benchmark": "aranza_memory_retrieval",
            "generated_at_epoch": int(time.time()),
            "execution": {"database": "temporary", "external_model_calls": False, "persistent_memory_changes": False},
            "cases": output_cases,
            "group_summary": group_summary,
            "caveat": "Las métricas dependen de las etiquetas humanas del escenario; evalúan recuperación, no comprensión semántica ni verdad.",
        }


def main_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", help="JSON con escenarios; si se omite, usa los escenarios integrados")
    parser.add_argument("--output", help="Ruta de salida JSON; si se omite, imprime en pantalla")
    args = parser.parse_args(argv)
    try:
        if args.cases:
            raw = json.loads(Path(args.cases).read_text(encoding="utf-8"))
            cases = _validate_cases(raw)
        else:
            cases = _validate_cases({"cases": DEFAULT_CASES})
        report = run(cases)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (OSError, json.JSONDecodeError, ScenarioError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main_cli())
