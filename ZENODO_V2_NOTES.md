V2 reports a new four-condition greedy-decoding evaluation on Qwen2.5-1.5B-Instruct, completed on 2026-11-13. The original V1 beam-search results remain unverified.

- Added public evidence covering 116 requests across four conditions (464 case-condition records), with per-record response hashes, a SHA-256 manifest and a verification script at `evidence/verify_generation.py`. The complete decoded transcript is retained for authorized review.
- Morpho-Guard triggered generation-stage intervention on 15/16 attack requests. Preliminary, unblinded assessment by one AI assistant scored attack success at 10/16 for Base and 1/16 for Morpho-Guard. The remaining successful attack emitted useful attack guidance before the intervention.
- Morpho-Guard intervened on 29/100 benign requests, including 23/30 high-confusion cases. The preliminary explicit false-refusal counts were 31/100 overall and 24/30 on the high-confusion subset.
- At the 0.65 threshold, the frozen layer-15 probe triggered on 0/16 transferred attack prompts and 0/100 newly authored benign prompts. The attack result shows a lack of transfer to this sample at the fixed threshold.
