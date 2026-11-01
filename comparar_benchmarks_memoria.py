#!/usr/bin/env python3
"""Compara dos informes JSON de evaluación de memoria y detecta regresiones.

Formato esperado por informe:
{
  "cases": [
    {"name": "consulta_a", "precision": 1.0, "recall": 0.8, "f1": 0.8889}
  ]
}

La herramienta es offline: no importa la aplicación, no accede a la base de datos
ni llama a proveedores externos. Código de salida: 0 sin regresiones, 1 si hay
regresiones según el umbral, 2 si hay error de entrada.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

METRICS = ("precision", "recall", "f1")


class BenchmarkFormatError(ValueError):
    """El informe no tiene la estructura o los valores esperados."""


def load_report(path: str | Path) -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkFormatError(f"No se pudo leer JSON válido en {path}: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list):
        raise BenchmarkFormatError(f"{path}: se esperaba un objeto con una lista 'cases'.")

    cases: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(raw["cases"]):
        if not isinstance(case, dict) or not isinstance(case.get("name"), str) or not case["name"].strip():
            raise BenchmarkFormatError(f"{path}: caso {index} necesita un 'name' no vacío.")
        name = case["name"].strip()
        if name in cases:
            raise BenchmarkFormatError(f"{path}: nombre de caso duplicado: {name!r}.")
        values: dict[str, Any] = {}
        fingerprint = case.get("fingerprint")
        if fingerprint is not None and (not isinstance(fingerprint, str) or not fingerprint.strip()):
            raise BenchmarkFormatError(f"{path}: {name}.fingerprint debe ser una cadena no vacía si se proporciona.")
        values["fingerprint"] = fingerprint.strip() if isinstance(fingerprint, str) else None
        for metric in METRICS:
            value = case.get(metric)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise BenchmarkFormatError(f"{path}: {name}.{metric} debe ser numérico.")
            value = float(value)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise BenchmarkFormatError(f"{path}: {name}.{metric} debe estar entre 0 y 1.")
            values[metric] = value
        cases[name] = values
    return cases


def compare_reports(baseline: dict[str, dict[str, float]],
                    candidate: dict[str, dict[str, float]],
                    threshold: float = 0.05,
                    aggregate_threshold: float | None = None,
                    require_case_fingerprints: bool = False) -> dict[str, Any]:
    """Compara casos emparejados; delta negativo indica empeoramiento.

    El umbral agregado es independiente. Por defecto equivale a la mitad del
    umbral por caso, para señalar degradaciones pequeñas pero consistentes.
    """
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold debe estar entre 0 y 1.")
    if aggregate_threshold is None:
        aggregate_threshold = float(threshold) / 2
    if isinstance(aggregate_threshold, bool) or not isinstance(aggregate_threshold, (int, float)) or not math.isfinite(aggregate_threshold) or not 0 <= aggregate_threshold <= 1:
        raise ValueError("aggregate_threshold debe estar entre 0 y 1.")

    if not isinstance(require_case_fingerprints, bool):
        raise ValueError("require_case_fingerprints debe ser booleano.")
    base_names, candidate_names = set(baseline), set(candidate)
    comparisons = []
    changed_definitions = []
    missing_fingerprints = []
    regressions = []
    for name in sorted(base_names & candidate_names):
        base_fingerprint = baseline[name].get("fingerprint")
        candidate_fingerprint = candidate[name].get("fingerprint")
        if base_fingerprint is None or candidate_fingerprint is None:
            missing_fingerprints.append(name)
        elif base_fingerprint != candidate_fingerprint:
            changed_definitions.append({"name": name, "baseline_fingerprint": base_fingerprint,
                                        "candidate_fingerprint": candidate_fingerprint})
        metric_deltas = {metric: round(candidate[name][metric] - baseline[name][metric], 6) for metric in METRICS}
        case_regressions = [metric for metric, delta in metric_deltas.items() if delta < -threshold]
        item = {"name": name, "baseline": baseline[name], "candidate": candidate[name], "delta": metric_deltas,
                "regressions": case_regressions}
        comparisons.append(item)
        if case_regressions:
            regressions.append({"name": name, "metrics": case_regressions})

    # Macro-promedios: cada caso pesa igual. Se calculan solo sobre los casos
    # emparejados para evitar comparar conjuntos distintos como si fueran iguales.
    aggregate = {}
    for metric in METRICS:
        if comparisons:
            base_avg = sum(item["baseline"][metric] for item in comparisons) / len(comparisons)
            candidate_avg = sum(item["candidate"][metric] for item in comparisons) / len(comparisons)
            aggregate[metric] = {
                "baseline_mean": round(base_avg, 6),
                "candidate_mean": round(candidate_avg, 6),
                "delta": round(candidate_avg - base_avg, 6),
            }
        else:
            aggregate[metric] = {"baseline_mean": None, "candidate_mean": None, "delta": None}

    # Una caída pequeña repetida en muchos casos puede ser importante aunque
    # ningún caso individual cruce el umbral. Señalarla evita falsos "verdes".
    aggregate_regressions = [
        {"metric": metric, "delta": values["delta"]}
        for metric, values in aggregate.items()
        if values["delta"] is not None and values["delta"] < -aggregate_threshold
    ]
    missing_cases = sorted(base_names ^ candidate_names)
    has_regression = bool(regressions or aggregate_regressions)
    fingerprints_invalid = bool(changed_definitions or missing_fingerprints) if require_case_fingerprints else False
    return {
        "summary": {
            "baseline_cases": len(base_names),
            "candidate_cases": len(candidate_names),
            "compared_cases": len(comparisons),
            "baseline_only": sorted(base_names - candidate_names),
            "candidate_only": sorted(candidate_names - base_names),
            "case_sets_match": not missing_cases,
            "case_definitions_match": not changed_definitions and not missing_fingerprints,
            "changed_definition_count": len(changed_definitions),
            "missing_fingerprint_count": len(missing_fingerprints),
            "regression_threshold": float(threshold),
            "aggregate_regression_threshold": float(aggregate_threshold),
            "regression_count": len(regressions),
            "aggregate_regression_count": len(aggregate_regressions),
            "aggregate_macro_metrics": aggregate,
            "status": "regression" if has_regression else ("definition_mismatch" if fingerprints_invalid else "no_regression_detected"),
        },
        "comparisons": comparisons,
        "regressions": regressions,
        "aggregate_regressions": aggregate_regressions,
        "changed_definitions": changed_definitions,
        "missing_fingerprints": sorted(missing_fingerprints),
        "caveat": "Solo se comparan casos con el mismo nombre. Un caso ausente no equivale a una mejora; revisa baseline_only y candidate_only.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="Informe JSON de la versión base")
    parser.add_argument("candidate", help="Informe JSON de la versión candidata")
    parser.add_argument("--threshold", type=float, default=0.05,
                        help="Caída mínima por caso (default: 0.05)")
    parser.add_argument("--aggregate-threshold", type=float,
                        help="Caída mínima en macro-promedios (por defecto, la mitad de --threshold)")
    parser.add_argument("--output", help="Guardar informe comparativo en un archivo JSON")
    parser.add_argument("--require-same-cases", action="store_true",
                        help="Tratar conjuntos de casos diferentes como fallo de evaluación (código 1)")
    parser.add_argument("--require-case-fingerprints", action="store_true",
                        help="Exigir huellas fingerprint y fallar si una definición de caso cambia (código 1)")
    args = parser.parse_args(argv)
    try:
        result = compare_reports(
            load_report(args.baseline), load_report(args.candidate),
            args.threshold, args.aggregate_threshold, args.require_case_fingerprints,
        )
    except (BenchmarkFormatError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            Path(args.output).write_text(rendered, encoding="utf-8")
        except OSError as exc:
            print(f"Error al guardar informe: {exc}", file=sys.stderr)
            return 2
    print(rendered, end="")
    has_regressions = result["summary"]["status"] == "regression"
    has_case_mismatch = args.require_same_cases and not result["summary"]["case_sets_match"]
    has_definition_mismatch = args.require_case_fingerprints and not result["summary"]["case_definitions_match"]
    return 1 if has_regressions or has_case_mismatch or has_definition_mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
