# HayosoAi Reopening Probe

**Version 0.1.0 · September 19, 2026 · Finite reference model and research-development artifact.**

When a reason for rejecting a route is withdrawn, what should a research process reconsider? This prototype makes one narrow part of that question executable. It is not a measurement of an AI model, a validated benchmark, or a claim to have solved alignment.

The code and examples were generated with ChatGPT under Zackary Loevseth's project direction. The list evaluator and bit-mask checker were produced in the same AI-assisted development process; different implementations are not independent human review. No external specialist review is claimed.

## Run it

Python 3.10 or newer; standard library only. The script makes no network requests, model calls, or external account actions.

```sh
python reopening_probe.py --self-test
python reopening_probe.py --cases > development_inputs.jsonl
python reopening_probe.py --answers > oracle_answers.jsonl
python reopening_probe.py --score oracle_answers.jsonl
```

The last command checks the scoring interface against its own reference answers. It is not a model evaluation. Do not use Python's `-O` flag for self-tests: the program refuses to claim success when assertions are disabled.

## A small information-loss result

Suppose two complete records initially have supported premises p, q, and r. Their reasons for exclusion are:

- A: `(p AND q) OR r`.
- B: `p OR (q AND r)`.

Both currently exclude the route. Both mention the same three premises. A handoff that retains only "excluded" and the unordered dependency list `{p,q,r}` cannot distinguish them.

Now withdraw support for p and q while keeping r supported. A still has a sufficient ground, r. B no longer has any supported ground. Under the declared rules, A remains excluded while B becomes eligible for reconsideration.

Therefore a deterministic updater given only the shared compressed record and the same update cannot always return the correct disposition for both histories. The missing information is the arrangement of the reasons, not merely their names.

This is an elementary counterexample about a specified lossy representation, not a novelty claim or an impossibility result for language models. A natural-language summary that faithfully preserves both logical structures can also retain the needed information. Whether a structured format helps real systems is a separate empirical question.

## Semantics

`grounds` is a list of sufficient support sets: the sets are alternatives (OR), and premises inside each set are jointly required (AND). A ground is live only when all its premises are marked `supported`.

`withdrawn` removes support without declaring a premise false. `refuted` is stored distinctly, although both are inactive for this support calculation. This is support bookkeeping under a supplied finite specification, not a general logic of truth or negation.

A live recorded ground returns `excluded_under_recorded_grounds`. With no live ground, a record declared complete **within its stated scope** returns `reconsider`; a partial record returns `insufficient_record`. Completeness is an input declaration, not something the script verifies about the world. The rule families include the empty alternative list (no recorded ground) and an empty sufficient set (unconditional recorded ground).

Revisions preserve the original reason structure and return a new record. This lets a later correction reconsider a second ground instead of inheriting only the previous verdict. The prototype does not store an unlimited history or discover unrecorded alternatives.

`candidate_acceptance` is always `not_derived`, and `execution_permission` is always `not_granted`. These fields make the scope explicit; they do not constitute a tested real-world permission enforcement system. Acceptance or execution would need a different, separately justified process.

## Actual local checks

The local run passed 540 state comparisons over all 20 nonredundant monotone rules on three premise-support bits and three recorded states per premise; 4,860 single-premise updates; and 540 JSON round trips. It also checked a successive-withdrawal/restoration sequence, partial-record behavior, six malformed inputs, and five deliberately wrong decision probes.

These counts describe finite software checks, not independent experimental samples, human participants, or LLM trials. The five probes distinguish OR/AND flattening, indiscriminate reopening, unjustified acceptance, and unjustified permission; they are not a comprehensive mutation-testing campaign. The public development generator emits 12 constructed fixtures. The scorer checks three required output fields, not prose quality or real external behavior.

Tested source SHA-256: `d0176557beb48e8a6687839a8dd06c365a081a72eacaac7887d6e8a74de0ea19`.

## Research next step

A useful pilot must separate preserving more information from formatting the same information differently. Compare faithful prose and structured records, with and without exclusion grounds, and keep a full-history reference condition. Use new held-out cases, matched resources, explicit model versions, and independent inspection of labels. Report null results and errors, not just successful corrections. The public fixtures here are development material, not held-out tests.

Prior-art comparison with truth maintenance, assumption-based reasoning, belief revision, and agent-memory evaluations remains necessary before making novelty claims. The new question is a candidate contribution, not proof that these fields have overlooked it.

## Participation and scope

A useful review could identify a semantic error, propose a fairer comparison, or contribute a counterexample where the retained record is inadequate. Please do not post private transcripts, credentials, employer data, or other people's personal information.

[HayosoAi project](../../README.md) · [Public participation thread](https://github.com/ZackaryLoevseth/research-portfolio/issues/5)

No new license is granted by this release, and no existing portfolio license is changed. Public inspectability is not a claim of an unrestricted reuse license. This artifact is separate from the original essay, the local Codex site, and Study 14.
