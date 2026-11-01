import json

import pytest

from ejecutar_benchmark_memoria import ScenarioError, _fingerprint, _validate_cases


def valid_case(**updates):
    case = {"name": "case_a", "query": "inglés conversación", "relevant": ["practicar inglés"], "irrelevant": ["sopa de verduras"]}
    case.update(updates)
    return case


def test_validates_manifest_and_applies_defaults():
    cases = _validate_cases({"cases": [valid_case()]})
    assert cases[0]["limit"] == 8
    assert cases[0]["category"] == "general"
    assert cases[0]["archive_relevant"] is False


def test_rejects_duplicate_scenario_names():
    with pytest.raises(ScenarioError, match="duplicado"):
        _validate_cases({"cases": [valid_case(), valid_case()]})


@pytest.mark.parametrize("case", [
    valid_case(query=""), valid_case(relevant=[]), valid_case(limit=0),
    valid_case(limit=True), valid_case(archive_relevant="yes"), valid_case(name=" "),
])
def test_rejects_invalid_scenarios(case):
    with pytest.raises(ScenarioError):
        _validate_cases({"cases": [case]})


def test_fingerprint_is_stable_for_key_order_and_changes_when_query_changes():
    case = _validate_cases({"cases": [valid_case()]})[0]
    reordered = dict(reversed(list(case.items())))
    assert _fingerprint(case) == _fingerprint(reordered)
    changed = dict(case, query="matemáticas")
    assert _fingerprint(case) != _fingerprint(changed)


def test_report_fingerprint_is_compatible_with_comparator(tmp_path):
    from comparar_benchmarks_memoria import load_report
    case = _validate_cases({"cases": [valid_case()]})[0]
    path = tmp_path / "report.json"
    path.write_text(json.dumps({"cases": [{"name": case["name"], "fingerprint": _fingerprint(case), "precision": 1, "recall": 1, "f1": 1}]}), encoding="utf-8")
    assert load_report(path)["case_a"]["fingerprint"].startswith("sha256:")


def test_group_defaults_and_is_in_fingerprint():
    case = _validate_cases({"cases": [valid_case()]})[0]
    assert case["group"] == "general"
    changed = dict(case, group="ambiguous")
    assert _fingerprint(case) != _fingerprint(changed)


@pytest.mark.parametrize("group", ["", "  ", "x" * 81, 12, None])
def test_rejects_invalid_group(group):
    with pytest.raises(ScenarioError, match="group"):
        _validate_cases({"cases": [valid_case(group=group)]})


def test_default_benchmark_has_grouped_metrics():
    from ejecutar_benchmark_memoria import DEFAULT_CASES
    cases = _validate_cases({"cases": DEFAULT_CASES})
    assert len(cases) >= 6
    assert {case["group"] for case in cases} >= {"direct_match", "normalization", "distractors"}
