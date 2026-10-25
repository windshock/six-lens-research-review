#!/usr/bin/env python3
"""Validate a small, machine-readable scientific review experiment record.

This checks completeness and whether a model-update claim has necessary gates.
It CANNOT verify the truth of evidence, dates, hashes, or raw experiments.

Usage:
  python scripts/validate_record.py references/review-record.example.json
  python scripts/validate_record.py --self-test
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

GATES = tuple(f"G{i}" for i in range(1, 7))
STATUSES = {"PASS", "FAIL", "NOT_TESTED", "NOT_APPLICABLE"}
SCOPES = {"target-proven", "lab-proven", "hypothesis-only"}
OUTCOMES = {
    "valid_same", "valid_distinguished", "unknown", "not_reached",
    "replay_invalid", "nondeterministic", "harness_failed", "no_treatment"
}


def nonempty_str(v):
    return isinstance(v, str) and bool(v.strip())


def validate_record(record):
    """Return a list of actionable validation failures."""
    errors = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    for field in ("experiment_id", "hypothesis_id", "source_commit", "next_query_reason"):
        if not nonempty_str(record.get(field)):
            errors.append(f"{field} must be a nonempty string")
    h = record.get("competing_hypotheses")
    if not isinstance(h, list) or len(h) < 2 or not all(nonempty_str(v) for v in h):
        errors.append("competing_hypotheses must contain at least two nonempty strings")
    elif len(h) != len(set(h)):
        errors.append("competing_hypotheses must not contain duplicate identifiers")
    predictions = record.get("predictions_before_run")
    if not isinstance(predictions, dict) or not predictions:
        errors.append("predictions_before_run must be an object")
    elif isinstance(h, list):
        for hypothesis in h:
            if not nonempty_str(predictions.get(hypothesis)):
                errors.append(f"missing preregistered prediction for {hypothesis}")
    q = record.get("query")
    if not isinstance(q, dict):
        errors.append("query must be an object")
        q = {}
    hash_value = q.get("replay_manifest_sha256")
    if not nonempty_str(hash_value) or not re.fullmatch(r"[a-fA-F0-9]{64}", hash_value):
        errors.append("query.replay_manifest_sha256 must be a 64-digit hex SHA256")
    if not isinstance(q.get("suffix"), list):
        errors.append("query.suffix must be a list (can be empty for observational experiment)")
    if q.get("mode") not in ("model_learning", "algorithm_comparison", "measurement_calibration"):
        errors.append("query.mode must be model_learning, algorithm_comparison, or measurement_calibration")
    gates = record.get("gates")
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        gates = {}
    for g in GATES:
        if gates.get(g) not in STATUSES:
            errors.append(f"gates.{g} must be one of {', '.join(sorted(STATUSES))}")
    outcome = record.get("outcome")
    if not isinstance(outcome, dict):
        errors.append("outcome must be an object")
        outcome = {}
    classification = outcome.get("classification")
    if classification not in OUTCOMES:
        errors.append("outcome.classification must be a documented outcome class")
    evidence = outcome.get("evidence_refs")
    if not isinstance(evidence, list) or not all(nonempty_str(v) for v in evidence):
        errors.append("outcome.evidence_refs must be a list of nonempty strings")
        evidence = []
    valid = classification in ("valid_same", "valid_distinguished")
    if valid:
        for g in ("G1", "G2", "G3"):
            if gates.get(g) != "PASS":
                errors.append(f"outcome {classification} requires {g}=PASS")
        if not evidence:
            errors.append(f"outcome {classification} requires raw evidence refs")
    model = record.get("model_update")
    if not isinstance(model, dict):
        errors.append("model_update must be an object")
        model = {}
    approved = model.get("approved")
    if not isinstance(approved, bool):
        errors.append("model_update.approved must be boolean")
    if approved:
        if classification != "valid_distinguished":
            errors.append("model update approval requires a valid_distinguished outcome")
        for g in ("G1", "G2", "G3", "G5", "G6"):
            if gates.get(g) != "PASS":
                errors.append(f"approved model update requires {g}=PASS")
        if record.get("predictions_frozen_before_run") is not True:
            errors.append("approved model update requires predictions_frozen_before_run=true")
        if not evidence:
            errors.append("approved model update requires evidence refs")
        if not nonempty_str(model.get("witness_ref")):
            errors.append("approved model update requires a witness_ref")
        if not nonempty_str(model.get("previous_version")) or not nonempty_str(model.get("new_version")):
            errors.append("approved model update requires previous_version/new_version")
        elif model["previous_version"] == model["new_version"]:
            errors.append("approved model update must change the model version")
    if record.get("claimed_algorithm_effect") is True:
        if q.get("mode") != "algorithm_comparison":
            errors.append("claimed_algorithm_effect requires query.mode=algorithm_comparison")
        if gates.get("G4") != "PASS" or gates.get("G5") != "PASS":
            errors.append("claimed_algorithm_effect requires G4 and G5 PASS")
        if record.get("treatment_activated") is not True:
            errors.append("claimed_algorithm_effect requires treatment_activated=true")
    # Optional conclusion-scope axis (security-hypothesis-lab vocabulary).
    scope = record.get("conclusion_scope")
    if scope is not None:
        if scope not in SCOPES:
            errors.append("conclusion_scope must be one of " + ", ".join(sorted(SCOPES)))
        premises = record.get("target_premises")
        if scope == "target-proven":
            if not isinstance(premises, dict) or not premises:
                errors.append("target-proven requires a nonempty target_premises object")
            elif not all(v is True for v in premises.values()):
                errors.append("target-proven requires every target premise confirmed (true)")
    return errors


def self_test():
    h = "a" * 64
    baseline = {
        "experiment_id": "SYNTH-1", "hypothesis_id": "H-SYNTH",
        "source_commit": "synthetic_fixture_no_commit", "competing_hypotheses": ["H0", "H1"],
        "predictions_before_run": {"H0": "same", "H1": "different"},
        "predictions_frozen_before_run": True,
        "query": {"mode": "model_learning", "replay_manifest_sha256": h, "suffix": [{"action": "probe"}]},
        "gates": {g: "PASS" for g in GATES},
        "outcome": {"classification": "valid_distinguished", "evidence_refs": ["synthetic-evidence"]},
        "model_update": {"approved": True, "previous_version": "v1", "new_version": "v2", "witness_ref": "synthetic-witness"},
        "next_query_reason": "test additional suffixes",
        "claimed_algorithm_effect": False,
    }
    tests = []
    tests.append(("valid synthetic witness", baseline, True))
    v = copy.deepcopy(baseline); v["outcome"]["classification"] = "unknown"
    tests.append(("unknown cannot approve split", v, False))
    v = copy.deepcopy(baseline); v["gates"]["G2"] = "NOT_TESTED"
    tests.append(("missing observation forbids split", v, False))
    v = copy.deepcopy(baseline); v["predictions_frozen_before_run"] = False
    tests.append(("posthoc prediction forbids split", v, False))
    v = copy.deepcopy(baseline); v["outcome"]["evidence_refs"] = []
    tests.append(("missing raw evidence forbids split", v, False))
    v = copy.deepcopy(baseline); v["claimed_algorithm_effect"] = True
    tests.append(("algorithm effect without correct mode forbidden", v, False))
    v = copy.deepcopy(baseline); v["outcome"]["classification"] = "no_treatment"; v["model_update"]["approved"] = False
    v["gates"]["G4"] = "NOT_APPLICABLE"; v["gates"]["G6"] = "NOT_APPLICABLE"
    tests.append(("no treatment remains a valid unapproved record", v, True))
    v = copy.deepcopy(baseline); v["conclusion_scope"] = "lab-proven"
    tests.append(("lab-proven scope accepted", v, True))
    v = copy.deepcopy(baseline); v["conclusion_scope"] = "target-proven"; v["target_premises"] = {"default_sapi": False}
    tests.append(("target-proven with unconfirmed premise forbidden", v, False))
    v = copy.deepcopy(baseline); v["conclusion_scope"] = "probably"
    tests.append(("unknown scope label forbidden", v, False))
    passed = 0
    for name, record, should_pass in tests:
        issues = validate_record(record)
        okay = (not issues) == should_pass
        print(("PASS" if okay else "FAIL") + " " + name)
        if not okay:
            print("  errors:", issues)
        passed += okay
    print(f"self_test={passed}/{len(tests)}")
    return 0 if passed == len(tests) else 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("record", nargs="?", help="JSON scientific experiment record")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.record:
        p.error("provide a JSON record path, or --self-test")
    try:
        data = json.loads(Path(a.record).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR reading record: {e}", file=sys.stderr)
        return 2
    issues = validate_record(data)
    if issues:
        print("INVALID RECORD:")
        for issue in issues:
            print("-", issue)
        return 1
    print("VALID RECORD SHAPE (not a verification of evidence truth)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
