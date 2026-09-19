# Pilot 01: the model mostly said “unknown”

**HayosoAi · September 19, 2026 · Completed exploratory receiver test. Negative for demonstrated efficacy.**

We ran 48 fresh-context inferences on a pinned Qwen3-0.6B model: 12 constructed cases, each represented as faithful prose, faithful JSON, flattened prose, and flattened JSON. The model answered `UNKNOWN` 46 times and `KEEP` twice. Both `KEEP` answers were wrong. Neither representation exceeded a constant-`UNKNOWN` baseline in its corresponding information condition.

**This pilot does not demonstrate that structured records improve model performance. It also does not establish equivalence between prose and JSON, or invalidate the separate finite information-loss example.** It establishes an actual, reproducible test execution and a failure to obtain informative receiver behavior under this configuration. We are preserving the result rather than selecting another model or prompt after the fact and calling that the same experiment.

## What happened

| Supplied memory | Correct / 12 | Always `UNKNOWN` / 12 | Actual answers |
| --- | ---: | ---: | --- |
| Reasons retained, prose | 2 | 2 | 12 `UNKNOWN` |
| Reasons retained, JSON | 2 | 2 | 10 `UNKNOWN`, 2 incorrect `KEEP` |
| Logical structure lost, prose | 9 | 9 | 12 `UNKNOWN` |
| Logical structure lost, JSON | 9 | 9 | 12 `UNKNOWN` |

All 48 outputs met the one-word format. None reached the 16-token output limit. Every generation ended after a label and the end-of-sequence token. The near-constant response therefore was not a case of the evaluator rejecting verbose answers or outputs being cut off at that limit. This does not establish that the allocated reasoning mode or prompt was adequate.

With reasons retained, KEEP and REOPEN were each correct in five cases; UNKNOWN in two. Always answering KEEP or always answering REOPEN would score 5/12 in those conditions. With the logical structure lost, uncertainty was the correct answer in nine cases. Its superficially higher score is not evidence that losing information helps: the correct-answer distribution and what the supplied information justifies have changed.

Within each information condition, prose and JSON had identical case-level correctness: two jointly correct cases with reasons, nine without. JSON changed two wrong UNKNOWN responses to wrong KEEP responses. No case switched between correct and incorrect across those representation pairs in this run.

### Case-level answers

K = KEEP, R = REOPEN, U = UNKNOWN. The expected answer for a flattened record is based on the information actually available, not the hidden original rule.

| Case | Expected, reasons | Prose | JSON | Expected, flat | Prose | JSON |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | K | U | U | U | U | U |
| C02 | R | U | U | U | U | U |
| C03 | R | U | K | U | U | U |
| C04 | K | U | U | U | U | U |
| C05 | K | U | U | K | U | U |
| C06 | R | U | K | R | U | U |
| C07 | R | U | U | U | U | U |
| C08 | R | U | U | R | U | U |
| C09 | K | U | U | U | U | U |
| C10 | K | U | U | U | U | U |
| C11 | U | U | U | U | U | U |
| C12 | U | U | U | U | U | U |

## What was tested—and what was not

The receiver reads a constructed prior exclusion and ordered premise updates. It must maintain an exclusion when an alternative sufficient reason survives, reconsider when a complete record loses all support, and answer UNKNOWN when its available record is insufficient. Reopening is never candidate acceptance or execution permission.

The four conditions cross preservation of AND/OR relationships with prose versus JSON representation. The prose and JSON counterparts preserve the same logical information, but are not token-length matched. Cases cover joint and alternative grounds, no change, complete withdrawal, repeated updates, restoration, partial records, and refutation.

There are 48 inferences but only 44 unique prompt texts: two pairs deliberately become identical under flattening in each representation. They are not 48 independent tasks. The oracle enumerates compatible monotone rules when relationships have been lost, so justified uncertainty receives credit.

This is not an evaluation of spontaneous summarization, a deployed memory product, frontier models, tool use, or human collaboration. No model created the handoffs, and no full-history reference condition was run. The cases are small constructed development inputs, not an independently validated benchmark or secret holdout. The pilot is separate from Study 14.

## Frozen protocol and execution evidence

The complete script, prompts, cases, model revision, decoding configuration, and labels were published before inference in [source commit bc2fa373](https://github.com/ZackaryLoevseth/research-portfolio/commit/bc2fa3733996253b1c65b22f6bc378bdd6407243). [Execution commit 2cc5704b](https://github.com/ZackaryLoevseth/research-portfolio/commit/2cc5704b7df5fc85a0a3e626ab0c21c532872eaf) added the bounded workflow. This is prospective commitment in a development repository, not formal preregistration.

[GitHub Actions run 35465749494](https://github.com/ZackaryLoevseth/research-portfolio/actions/runs/35465749494), job 105957637995, completed all 48 inferences on September 19, 2026. The final result was logged at 19:56:49 UTC, or 12:56 p.m. Pacific. The raw report was recovered from the workflow's lossless compressed log payload; it is not a reconstruction from the summary table.

Model: [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B), revision `c1899de289a04d12100db370d81485cdf75e47ca`. CPU float32, four threads; PyTorch 2.8.0+cpu, Transformers 4.56.2, Python 3.12.3. Non-thinking mode; sampling temperature 0.7, top-p 0.8, top-k 20, maximum 16 new tokens. Seed 20260919 was reset for each inference; inference order was shuffled with that seed. There was one sample per case-condition, not a sampling-distribution estimate.

Actual loaded parameter count: 596,049,920. Recorded model-load time: 10.3094 seconds. Inference-loop time: 116.5655 seconds. Total recorded input tokens: 16,728; output tokens including termination: 96. Setup and downloads are outside the inference-loop timing. No paid inference service or user API key was used. Energy, water, and emissions are unmeasured.

Code, cases, checking, and analysis are AI-authored under Zackary Loevseth's project direction. Different checking implementations from this same process are not independent human review. No novelty, third-party endorsement, general safety, or efficacy claim is established.

## Inspect the entire report without running a model

The complete original JSON report is preserved losslessly in [raw_report.b64](raw_report.b64), using zlib compression followed by base64. [review_results.py](review_results.py) verifies its hash, reconstructs `pilot_results.json`, compares every output against the frozen manifest, and recomputes the scores. This only uses Python's standard library and makes no network or model calls.

From this directory:

```sh
python review_results.py
python handoff_pilot.py --manifest > pilot_manifest.json
```

The JSON includes every raw answer, generated token IDs, expected labels, input/output token counts, prompt hashes, latency, truncation flags, and runtime metadata. The manifest contains all stimuli and instructions. Do not expose expected labels to a receiver when running a new experiment.

Integrity references:

- Frozen script SHA-256: `ded05a8eff2c5bd4afa93cfb2290cd1600afc97dfdb0ea4e20481bad2c287e16`.
- Canonically serialized manifest SHA-256: `58aaeb440ee96706a069951c95edeec06cc6829ff0bb5709ed6baea1ec06624f`.
- Original 29,981-byte raw report SHA-256: `1a93c668f51fc93f85bc9feab8978e8e1365b8546410dcc41ae54cb3ed3473a1`.

The reader checks integrity and rescoring; it does not independently establish whether the task specification is the right one. Review the oracle as well as the totals.

## Decision from this pilot

Do not promote an improvement claim or scale this unchanged experiment. The next justified technical step is a diagnostic preflight: establish whether the receiver can solve simple complete-record controls, separate those from incomplete-record uncertainty, counterbalance output labels, and examine sensitivity to prompt complexity and reasoning mode. Any changed prompt, model, or decoding configuration must become a separately documented experiment. Keep this run visible.

An implementation direction worth testing is to let a model propose or extract a record, validate that extraction against its source, and let a deterministic evaluator handle explicit support bookkeeping. The present result does not prove that architecture works; it helps locate the questions that architecture must answer. The difficult work includes recovering valid grounds from language, knowing what was omitted, and checking the declared coverage—not merely executing AND and OR.

The mathematical point and the empirical question remain distinct: preserving enough information makes correct revision possible, but does not guarantee that a particular model will use it correctly.

[Reference model and finite audit](../README.md) · [Public participation](https://github.com/ZackaryLoevseth/research-portfolio/issues/5)

No model weights or private application materials are included. No new license is granted by this report, and no existing portfolio licenses or scientific releases are changed.
