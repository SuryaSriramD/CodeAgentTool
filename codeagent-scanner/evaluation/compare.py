"""Offline comparison of labeled cases with synthetic or explicitly recorded results.

This program has no model-client imports or network operations. Default sample
records exercise metric calculation only; their values are NOT benchmark results.
"""

import argparse
import json
from pathlib import Path


MODES = ("static", "single_agent", "multi_agent")


def synthetic_records(cases):
    """Illustrative, intentionally arbitrary outcomes; never model observations."""
    records = []
    for mode_index, mode in enumerate(MODES):
        for index, case in enumerate(cases):
            # Identical classification errors across modes intentionally avoid a
            # manufactured claim that adding agents improves model quality.
            positive = case["vulnerable"] or index == 1
            records.append({"case_id": case["id"], "mode": mode, "positive": positive,
                            "reviewed_proposals": int(positive and mode == "multi_agent"),
                            "unresolved_proposals": 0,
                            "latency_ms": 100 * (mode_index + 1),
                            "tokens": 0 if mode == "static" else 100 * mode_index})
    return {"origin": "synthetic", "records": records}


def compare(corpus, observations):
    if observations.get("origin") not in {"synthetic", "recorded"}:
        raise ValueError("Records must declare origin=synthetic or recorded")
    labels = {case["id"]: case["vulnerable"] for case in corpus["cases"]}
    if len(labels) != len(corpus["cases"]) or not labels:
        raise ValueError("Corpus case IDs must be unique and nonempty")
    buckets = {mode: [] for mode in MODES}
    seen = set()
    for row in observations["records"]:
        identity = (row["mode"], row["case_id"])
        if row["mode"] not in buckets or row["case_id"] not in labels or identity in seen:
            raise ValueError("Unknown mode/case or duplicate observation")
        if type(row["positive"]) is not bool:
            raise ValueError("positive must be a boolean classification")
        for field in ("reviewed_proposals", "unresolved_proposals", "latency_ms", "tokens"):
            if not isinstance(row[field], (int, float)) or row[field] < 0:
                raise ValueError(f"{field} must be a nonnegative observation")
        seen.add(identity)
        buckets[row["mode"]].append(row)
    result = {"origin": observations["origin"],
              "synthetic_not_model_quality": observations["origin"] == "synthetic",
              "patches_applied_or_tested": False, "modes": {},
              "limitations": "Small isolated labels; reviewed proposals are not validated fixes. Latency and tokens describe the supplied records only."}
    for mode, rows in buckets.items():
        if len(rows) != len(labels):
            raise ValueError(f"Mode {mode} needs one observation per corpus case")
        tp = sum(row["positive"] and labels[row["case_id"]] for row in rows)
        fp = sum(row["positive"] and not labels[row["case_id"]] for row in rows)
        fn = sum(not row["positive"] and labels[row["case_id"]] for row in rows)
        result["modes"][mode] = {
            "cases": len(rows), "true_positives": tp, "false_positives": fp, "false_negatives": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "reviewed_proposals": sum(row["reviewed_proposals"] for row in rows),
            "unresolved_proposals": sum(row["unresolved_proposals"] for row in rows),
            "mean_latency_ms": sum(row["latency_ms"] for row in rows) / len(rows),
            "total_tokens": sum(row["tokens"] for row in rows),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).with_name("corpus.json"))
    parser.add_argument("--records", type=Path, help="Offline JSON observations with explicit origin")
    args = parser.parse_args()
    corpus = json.loads(args.corpus.read_text())
    observations = json.loads(args.records.read_text()) if args.records else synthetic_records(corpus["cases"])
    print(json.dumps(compare(corpus, observations), indent=2))


if __name__ == "__main__":
    main()
