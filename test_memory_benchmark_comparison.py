import json
from pathlib import Path

import pytest

from comparar_benchmarks_memoria import BenchmarkFormatError, compare_reports, load_report


def report(**cases):
    return {name: {"precision": vals[0], "recall": vals[1], "f1": vals[2]} for name, vals in cases.items()}


def test_detects_metric_regression_for_matching_case():
    result = compare_reports(report(search=(1, 1, 1)), report(search=(1, 0.7, 0.82)))
    assert result["summary"]["status"] == "regression"
    assert result["regressions"] == [{"name": "search", "metrics": ["recall", "f1"]}]


def test_small_change_below_threshold_is_not_flagged():
    result = compare_reports(report(search=(1, 0.9, 0.95)), report(search=(1, 0.87, 0.93)))
    assert result["summary"]["regression_count"] == 0


def test_reports_cases_missing_from_either_version_without_calling_them_improvements():
    result = compare_reports(report(old=(1, 1, 1)), report(new=(1, 1, 1)))
    assert result["summary"]["baseline_only"] == ["old"]
    assert result["summary"]["candidate_only"] == ["new"]
    assert result["summary"]["compared_cases"] == 0
    assert "no equivale a una mejora" in result["caveat"]


def test_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        compare_reports({}, {}, 1.1)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.1, 1.1, True])
def test_rejects_invalid_metric_values(tmp_path, bad):
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"cases": [{"name": "x", "precision": bad, "recall": 1, "f1": 1}]}), encoding="utf-8")
    with pytest.raises(BenchmarkFormatError):
        load_report(path)


def test_rejects_duplicate_case_names(tmp_path):
    path = tmp_path / "report.json"
    case = {"name": "x", "precision": 1, "recall": 1, "f1": 1}
    path.write_text(json.dumps({"cases": [case, case]}), encoding="utf-8")
    with pytest.raises(BenchmarkFormatError):
        load_report(path)


def test_reports_macro_average_for_matched_cases_only():
    result = compare_reports(
        report(a=(1.0, 0.8, 0.9), b=(0.5, 0.4, 0.45)),
        report(a=(1.0, 0.9, 0.95), b=(0.5, 0.2, 0.3), only_new=(1, 1, 1)),
    )
    aggregate = result["summary"]["aggregate_macro_metrics"]
    assert aggregate["precision"]["delta"] == 0.0
    assert aggregate["recall"]["baseline_mean"] == 0.6
    assert aggregate["recall"]["candidate_mean"] == 0.55
    assert result["summary"]["case_sets_match"] is False


def test_empty_matched_set_has_null_aggregate_not_fake_zero():
    result = compare_reports(report(old=(1, 1, 1)), report(new=(1, 1, 1)))
    assert result["summary"]["aggregate_macro_metrics"]["f1"]["delta"] is None


def test_cli_require_same_cases_fails_on_mismatch(tmp_path):
    import comparar_benchmarks_memoria as cli
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    baseline.write_text(json.dumps({"cases": [{"name": "old", "precision": 1, "recall": 1, "f1": 1}]}), encoding="utf-8")
    candidate.write_text(json.dumps({"cases": [{"name": "new", "precision": 1, "recall": 1, "f1": 1}]}), encoding="utf-8")
    assert cli.main([str(baseline), str(candidate), "--require-same-cases"]) == 1


def test_detects_aggregate_regression_when_many_small_drops_accumulate():
    baseline = report(a=(1.0, 1.0, 1.0), b=(1.0, 1.0, 1.0), c=(1.0, 1.0, 1.0))
    candidate = report(a=(1.0, 0.96, 0.98), b=(1.0, 0.96, 0.98), c=(1.0, 0.96, 0.98))
    result = compare_reports(baseline, candidate, threshold=0.05)
    assert result["summary"]["regression_count"] == 0
    assert result["summary"]["aggregate_regression_count"] == 1
    assert {item["metric"] for item in result["aggregate_regressions"]} == {"recall"}
    assert result["summary"]["status"] == "regression"


def test_aggregate_regression_changes_cli_exit_code(tmp_path):
    import comparar_benchmarks_memoria as cli
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    baseline.write_text(json.dumps({"cases": [
        {"name": name, "precision": 1, "recall": 1, "f1": 1}
        for name in ("a", "b", "c")
    ]}), encoding="utf-8")
    candidate.write_text(json.dumps({"cases": [
        {"name": name, "precision": 1, "recall": 0.96, "f1": 0.98}
        for name in ("a", "b", "c")
    ]}), encoding="utf-8")
    assert cli.main([str(baseline), str(candidate), "--threshold", "0.05"]) == 1


def test_detects_changed_case_fingerprint():
    baseline = {"search": {"precision": 1, "recall": 1, "f1": 1, "fingerprint": "query-v1"}}
    candidate = {"search": {"precision": 1, "recall": 1, "f1": 1, "fingerprint": "query-v2"}}
    result = compare_reports(baseline, candidate, require_case_fingerprints=True)
    assert result["summary"]["case_definitions_match"] is False
    assert result["changed_definitions"] == [{
        "name": "search", "baseline_fingerprint": "query-v1", "candidate_fingerprint": "query-v2"
    }]
    assert result["summary"]["status"] == "definition_mismatch"


def test_strict_fingerprint_mode_rejects_missing_fingerprints():
    result = compare_reports(report(search=(1, 1, 1)), report(search=(1, 1, 1)), require_case_fingerprints=True)
    assert result["summary"]["missing_fingerprint_count"] == 1
    assert result["summary"]["status"] == "definition_mismatch"


def test_fingerprint_metadata_is_optional_for_legacy_reports(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"cases": [{"name": "x", "precision": 1, "recall": 1, "f1": 1, "fingerprint": "  abc  "}]}), encoding="utf-8")
    loaded = load_report(path)
    assert loaded["x"]["fingerprint"] == "abc"


def test_rejects_empty_fingerprint(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"cases": [{"name": "x", "precision": 1, "recall": 1, "f1": 1, "fingerprint": "  "}]}), encoding="utf-8")
    with pytest.raises(BenchmarkFormatError):
        load_report(path)


def test_cli_strict_fingerprints_fails_when_definitions_changed(tmp_path):
    import comparar_benchmarks_memoria as cli
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    baseline.write_text(json.dumps({"cases": [{"name": "x", "precision": 1, "recall": 1, "f1": 1, "fingerprint": "old"}]}), encoding="utf-8")
    candidate.write_text(json.dumps({"cases": [{"name": "x", "precision": 1, "recall": 1, "f1": 1, "fingerprint": "new"}]}), encoding="utf-8")
    assert cli.main([str(baseline), str(candidate), "--require-case-fingerprints"]) == 1
