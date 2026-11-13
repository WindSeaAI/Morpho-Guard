# Morpho-Guard

Morpho-Guard studies relational constraints for model generation. This repository currently provides a prompt-level regex pilot and its measured results.

## Pilot method

The extractor looks for English action and system-critical target signals anywhere in the prompt. The gate triggers when both signals are present and the caller has supplied no verified authorization. All benchmark requests use unverified authorization. Quoted text, negation, and unrelated matches can trigger the rule. The benchmark calls the gate directly and records its decision without model inference.

The test uses 16 transferred JailbreakBench attack prompts, 100 newly authored benign prompts including 30 high-confusion prompts, and five separate development checks. The benign and development fixtures were authored alongside the implementation. The transferred attacks were known during development. The evaluation is exploratory.

## Results

| Split | Gate triggers | Trigger rate |
| --- | ---: | ---: |
| External attack prompts | 11/16 | 68.75% |
| Benign prompts | 16/100 | 16% |
| High-confusion benign subset | 16/30 | 53.33% |

The ungated baseline has no gate and therefore no gate triggers. The pilot measures rule triggers. Response refusals, attack success, generation-stage pruning, and the planned probe and combined arms require a separate model-based run.

## Reproduce

Use Python 3.11 or newer. The pilot uses the Python standard library.

```bash
python public/run_comparison.py --output /tmp/morpho-gate-reproduction.json
```

Choose a new output filename for each run. The [recorded run](evidence/regex_gate_20261112.json) includes per-case decisions and SHA-256 hashes. [REPRODUCTION.md](REPRODUCTION.md) records the validation procedure and the historical scaffold audit.

The preceding lexical-mask and activation-probe experiments are documented in the [guardrail-ood-eval repository](https://github.com/WindSeaAI/guardrail-ood-eval).

## Manuscript citation

```bibtex
@unpublished{liu2026morphoguard,
  title = {From External Probes to Structural Pruning: Verification of Generation-Stage Blocking via Morpho-Root Relational Constraints},
  author = {Liu, Shen and Zeng, Jialiang},
  year = {2026},
  note = {Research manuscript draft}
}
```

## New generation-stage experiment

`public/run_generation_comparison.py` evaluates Base, Probe, Morpho-Guard, and Probe + Morpho on local Qwen2.5-1.5B-Instruct with the frozen layer-15 probe. Use Python 3.11+, PyTorch 2.7.1, Transformers 4.57.6 and CUDA. The runner checks the model and probe weight hashes and records per-case results in JSONL.

This implementation checks the generated prefix during greedy decoding. On a rule trigger it masks every alternative next-token score, forces a fixed refusal continuation, and ends with EOS when the generation budget allows. The already generated prefix is retained in the evaluation record. This experiment uses greedy decoding. The manuscript's Beam Search implementation and original evaluation assets have yet to be recovered.

```bash
python public/run_generation_comparison.py \
  --model /root/autodl-tmp/models/Qwen2.5-1.5B-Instruct \
  --probe /root/autodl-tmp/MorphoProbe_Phase2_v0.1/results/probe_v2_train_20261107T040555268047Z/probe.pt \
  --output /root/autodl-tmp/morpho-generation-smoke.jsonl --smoke
```

The smoke run evaluates one development case under all four conditions. To run the 116 evaluation cases, remove `--smoke` and choose a fresh output file. The run is complete when its final JSONL row reports `"complete": true` and there are 464 per-condition records. Inspect raw responses privately and score refusal and attack success separately from interventions. These newly authored benign cases are exploratory. The full generation run completed on 2026-11-13. See the results below.

### Generation results on RTX 6000D

Each condition used the same 16 transferred attacks and 100 newly authored benign requests. Decoding was greedy with up to 512 new tokens. The probe threshold was 0.65.

| Condition | Probe blocks on attacks | Generation interventions on attacks | Attack success (preliminary) | Explicit false refusals, ordinary | Explicit false refusals, high-confusion | Explicit false refusals, overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base | — | — | 10/16 | 1/70 | 1/30 | 2/100 |
| Probe | 0/16 | — | 10/16 | 1/70 | 1/30 | 2/100 |
| Morpho-Guard | — | 15/16 | 1/16 | 7/70 | 24/30 | 31/100 |
| Probe + Morpho | 0/16 | 15/16 | 1/16 | 7/70 | 24/30 | 31/100 |

The probe triggered on none of the 116 cases. The structural rule intervened on 29 benign requests, with 6 ordinary and 23 high-confusion cases. Two other benign requests received spontaneous refusals in all conditions. The one attack without structural intervention received a spontaneous refusal. One intervened attack retained materially useful attack guidance in the generated prefix.

See the [scoring protocol](REPRODUCTION.md#generation-stage-run-of-2026-11-13), [case-level labels](evidence/generation_20261113_labels.csv), and [run manifest and metrics](evidence/generation_20261113_summary.json). The response scores are a preliminary unblinded assistant review. The manuscript's original run remains unverified.
