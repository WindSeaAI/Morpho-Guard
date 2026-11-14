"""Check public evidence, optionally against the private inference transcript."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = ROOT / "evidence"
ARMS = ("base", "probe", "morpho", "probe_morpho")
DATA = dict(attack="jbb_attacks.json", benign="benign_prompts.json", dev="dev_prompts.json")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(test, message):
    if not test:
        raise SystemExit(message)


def project(row):
    return {**{k: v for k, v in row.items() if k != "output"},
            "output_sha256": digest(row["output"].encode("utf-8"))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path)
    args = parser.parse_args()
    manifest = json.loads((E / "MANIFEST.json").read_text())
    for name, item in manifest.items():
        data = (ROOT / name).read_bytes()
        require(len(data) == item["bytes"] and digest(data) == item["sha256"], f"File mismatch: {name}")
    summary = json.loads((E / "generation_20261113_summary.json").read_text())
    rows = [json.loads(line) for line in (E / "generation_20261113_records.jsonl").read_text().splitlines()]
    expected = {}
    for split in ("attack", "benign"):
        for r in json.loads((ROOT / "data" / DATA[split]).read_text()):
            expected[r["id"]] = (split, r.get("high_confusion", False))
    keys = {(r["id"], r["arm"]) for r in rows}
    require(len(rows) == len(keys) == 464 and keys == {(i, a) for i in expected for a in ARMS},
            "Unexpected or duplicate record keys")
    with (E / "generation_20261113_labels.csv").open(newline="") as f:
        labels = {(r["case_id"], r["arm"]): r for r in csv.DictReader(f)}
    require(set(labels) == keys, "Label keys mismatch")
    for row in rows:
        key = row["id"], row["arm"]
        label = labels[key]
        require((row["split"], row["high_confusion"]) == expected[key[0]], f"Wrong split: {key}")
        step = row["generation_trigger_step"]
        require(row["output_sha256"] == label["output_sha256"]
                and row["probe_score"] == float(label["probe_score"])
                and str(row["probe_blocked"]) == label["probe_blocked"]
                and ("" if step is None else str(step)) == label["generation_trigger_step"],
                f"Record/label mismatch: {key}")
    for arm in ARMS:
        for group, metrics in summary["metrics"][arm].items():
            subset = [r for r in rows if r["arm"] == arm and (
                r["split"] == "attack" if group == "attack" else r["split"] == "benign" and (
                    group == "all_benign" or r["high_confusion"] == (group == "high_confusion_benign")))]
            label_field = "attack_success" if group == "attack" else "explicit_false_refusal"
            actual = dict(total=len(subset), probe_blocks=sum(r["probe_blocked"] for r in subset),
                          generation_interventions=sum(r["generation_trigger_step"] is not None for r in subset))
            actual["attack_successes" if group == "attack" else "explicit_false_refusals"] = sum(labels[r["id"], arm][label_field] == "True" for r in subset)
            require(actual == metrics, f"Summary mismatch: {arm}/{group}")
    print("PASS: file hashes, 464 case-condition records, published labels and summary counts")
    if args.raw:
        data = args.raw.read_bytes()
        require(digest(data) == summary["uploaded_log_sha256"], "Private transcript hash mismatch")
        raw = [json.loads(line) for line in data.decode("utf-8-sig").splitlines() if line.strip()]
        require(raw[0]["manifest"] == summary["manifest"] and raw[-1] == {"complete": True}
                and [project(r) for r in raw[1:-1]] == rows, "Private transcript does not match public records")
        print("PASS: private transcript and all 464 response hashes match")


if __name__ == "__main__":
    main()
