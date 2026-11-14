# Generation evidence (2026-11-13)

The RTX 6000D run evaluated 16 attacks and 100 benign requests under four
conditions. The historical prompt-only pilot is a separate experiment.

- [Per-condition records](generation_20261113_records.jsonl): 464 rows keyed
  by case ID and arm, with probe decisions, generation trigger steps, token
  counts, refusal sequence completion and decoded response SHA-256.
  Case IDs link to the prompts in [data](../data/).
- [Response labels](generation_20261113_labels.csv): preliminary, unblinded
  assistant judgments with reasons for all 464 rows.
- [Run summary](generation_20261113_summary.json): runtime, settings, model,
  probe, data and source hashes, and aggregate counts.
- [Manifest](MANIFEST.json): hashes and byte counts for the public generation
  evidence and the code and input files identified by the run.

From the repository root, run `python evidence/verify_generation.py`. This
checks file integrity, per-condition coverage, record/label agreement and
recomputes the reported counts. It does not run model inference or validate
the correctness of the qualitative judgments.

The original JSONL includes the complete decoded responses and is retained
privately because it contains potentially harmful generated material. An
authorized reviewer with the archived transcript can run
`python evidence/verify_generation.py --raw /path/to/full.jsonl`; this also
checks the transcript hash and reconstructs the public records from it.
The public records omit only the response text from each per-condition row
and replace it with its SHA-256. The trigger step is the recorded
intervention event; this run did not log every token's logits. See the
[root README](../README.md) for GPU rerun instructions.
