"""Compare an ungated baseline and the regex gate without generating responses."""

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from . import graph_builder, morpho_guard
else:
    import graph_builder
    import morpho_guard

ROOT = Path(__file__).resolve().parents[1]


def load_cases(path, expected):
    raw = path.read_bytes()
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != expected:
        raise ValueError(f"{path}: expected {expected} cases")
    for row in rows:
        if (not isinstance(row, dict)
                or not isinstance(row.get("id"), str) or not row["id"]
                or not isinstance(row.get("text"), str) or not row["text"].strip()):
            raise ValueError(f"{path}: each case needs a non-empty id and text")
    return rows, hashlib.sha256(raw).hexdigest()


def count(rows, predicate):
    matched = [row for row in rows if predicate(row)]
    return {
        "total": len(matched),
        "triggered": sum(row["structural_gate"]["triggered"] for row in matched),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/jbb_attacks.json")
    parser.add_argument("--benign", type=Path, default=ROOT / "data/benign_prompts.json")
    parser.add_argument("--dev", type=Path, default=ROOT / "data/dev_prompts.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    attacks, attack_hash = load_cases(args.dataset, 16)
    benign, benign_hash = load_cases(args.benign, 100)
    dev, dev_hash = load_cases(args.dev, 5)
    all_cases = attacks + benign + dev
    if len({row["id"] for row in all_cases}) != len(all_cases):
        parser.error("Duplicate IDs across datasets")
    if len({row["text"].strip() for row in all_cases}) != len(all_cases):
        parser.error("Duplicate prompt text across datasets")
    if any(type(row.get("high_confusion")) is not bool for row in benign):
        parser.error("Each benign case needs a boolean high_confusion field")
    if sum(row["high_confusion"] for row in benign) != 30:
        parser.error("Expected 30 high-confusion benign cases")

    records = []
    for split, cases in (("attack", attacks), ("benign", benign)):
        for case in cases:
            records.append({
                "id": case["id"],
                "split": split,
                "high_confusion": case.get("high_confusion", False),
                "baseline_gate_triggered": False,
                "structural_gate": morpho_guard.evaluate_gate(case["text"]),
            })

    report = {
        "scope": "Prompt-level rule triggers only",
        "rule_version": morpho_guard.RULE_VERSION,
        "authorization_context": "Unverified for every evaluated request",
        "input_sha256": {"attack": attack_hash, "benign": benign_hash, "dev": dev_hash},
        "source_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), Path(graph_builder.__file__), Path(morpho_guard.__file__))
        },
        "counts": {
            "attack": count(records, lambda row: row["split"] == "attack"),
            "benign": count(records, lambda row: row["split"] == "benign"),
            "high_confusion_benign": count(records, lambda row: row["high_confusion"]),
        },
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(report["counts"], indent=2))
    print(f"Evidence: {args.output}")


if __name__ == "__main__":
    main()
