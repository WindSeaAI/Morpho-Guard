# Morpho-Guard reproduction status

Audit date: 2026-11-12. Public revision inspected: `9de0b6837bb68b3af9f849bc7b84fcf92cbd4fc4`.

## Clean clone preflight

A clean clone succeeded. The following commands were executed against the inspected revision with local Python.

| Command | Exit code | Observed output |
| --- | --- | --- |
| `python public/graph_builder.py` | 1 | `Not implemented: relational node extraction.` |
| `python public/morpho_guard.py` | 1 | `Not implemented: generation-stage logits pruning.` |
| `python public/run_comparison.py` | 1 | `Not implemented: four-condition evaluation.` |

| Data file | Verified count | SHA-256 |
| --- | ---: | --- |
| `data/jbb_attacks.json` | 16 attack prompts with distinct IDs | `6e27ab9e85cfa8df34e4dcd6c1c1004d456979a061384d0156c7e317d6422c36` |
| `data/benign_prompts.json` | 0 | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| `data/dev_prompts.json` | 0 | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |

## Pending validation

Recover the experiment implementation and the original benign and development datasets, or document a new implementation and evaluation protocol as a new run. Record the extractor revision, authorization inputs, model and checkpoint hashes, decoding configuration, and dataset hashes. Verify the structural rule and refusal or termination behavior, then run the baseline, probe, structural rule, and combined conditions. Record per-case interventions, response judgments, and generation errors. Calculate gate triggers and response-level outcomes separately, including the benign high-confusion subset.

The supplied draft's 16/16 structural blocking remains unverified. The draft's 6/30 corresponds to 20%. If those six samples belong to the 100-sample benign set, the overall false refusal rate is at least 6%.

The 199/200 lexical comparison and 0/16 external probe gate triggers are results of the preceding experiments documented in the separate [guardrail-ood-eval repository](https://github.com/WindSeaAI/guardrail-ood-eval).
