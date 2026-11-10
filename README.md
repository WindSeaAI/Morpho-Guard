# Morpho-Guard

**Research scaffold.** Morpho-Guard is a proposed evaluation of relational constraints during generation. This README records the intended mechanism, comparison design, and results that require run evidence before publication.

The preceding evaluation of the frozen layer-15 activation probe recorded `0/16` gate triggers on the selected transferred attacks. The new experiment asks whether a scoped relational rule changes those outcomes and how often it interrupts valid system-administration requests.

## Mechanism under evaluation

The draft specifies a rule-based extractor for system operations. It represents a candidate action, its target, and the authorization status in the configured evaluation environment.

| Field | Example values |
| --- | --- |
| Action `A` | Execute, delete, escalate |
| Target `T` | System-critical resource, user data |
| Authorization `U` | Verified, unverified |

The proposed rule rejects a transition with `A = Execute` and `T = System_Critical` when `U` is unverified. The implementation should make its authorization inputs explicit and record each rule decision. A decoding implementation must retain a valid refusal continuation or end generation explicitly when applying the rule. An all-masked logit vector cannot be sampled as an ordinary token distribution.

The extractor in the supplied design uses regex and keyword heuristics. The proposed reachability claim concerns the states and transitions defined by that extractor and the enforced rule. Verify those definitions and the enforcement before making claims about semantic safety.

## Comparison design

Compare the base model, the activation probe, the structural rule, and the combined condition. The supplied design specifies 16 external attack prompts and 100 benign prompts, including 30 high-confusion cases. Freeze the rule on the separate development set before evaluating these prompts. Record the version of the rule, input ID, intervention, generated answer, and outcome for each condition.

Report the gate-trigger rate, answer refusal rate, and attack success separately. Gate triggers describe the intervention. Attack success depends on judging the resulting answer against the attack goal. For benign requests, record the denominator for both the full set and the high-confusion subset.

## Results to verify

| Item in the supplied draft | Review status |
| --- | --- |
| Structural rule and combined condition each block `16/16` attacks | Check against the actual comparison logs and each request's recorded decision. |
| High-confusion false refusals recorded as `2% (6/30)` | The fraction `6/30` equals `20%`. Confirm the six underlying cases before reporting the rate. |
| Overall benign false refusals recorded as `0%` | If the six cases belong to the 30-case subset of these 100 prompts, the overall rate is at least `6/100 (6%)`. It is exactly `6%` if the other 70 prompts have zero false refusals. |

The existing negative-result evidence covers the lexical-mask and activation-probe runs. Add the structural-rule run manifest and per-request records before filling a results table for the new conditions.

## Repository structure

```text
public/
    morpho_guard.py
    graph_builder.py
    run_comparison.py
data/
    jbb_attacks.json
    benign_prompts.json
    dev_prompts.json
    external_source.json
    JBB_ARTIFACTS_LICENSE.txt
requirements.txt
README.md
SECURITY.md
LICENSE
```

The Python modules are explicit placeholders for the implementation. The attack
set contains 16 transferred prompts from the previous evaluation. The source
manifest describes the original mixed set, including its benign controls.
The benign and development JSON files currently contain empty arrays. The
planned counts are 100 benign prompts, including 30 high-confusion prompts, and
5 separate development prompts. The dependency list is preliminary.

Related experiment materials are available in the
[guardrail-ood-eval repository](https://github.com/WindSeaAI/guardrail-ood-eval).

## Manuscript citation

```bibtex
@unpublished{liu2026morphoguard,
  title = {From External Probes to Structural Pruning: Verification of Generation-Stage Blocking via Morpho-Root Relational Constraints},
  author = {Liu, Shen and Zeng, Jialiang},
  year = {2026},
  note = {Research manuscript draft}
}
```
