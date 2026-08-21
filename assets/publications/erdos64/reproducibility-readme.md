# Excess-Degree Bounds for Minimal Erdős–Gyárfás Counterexamples

> **PUBLICATION-READY PREPRINT — EXTERNAL SPECIALIST REVIEW PENDING**

The Erdős–Gyárfás conjecture remains open. This repository publishes a
conditional structural theorem about a hypothetical counterexample chosen
first by minimum order and then, subject to that, by minimum size.

Let

\[
A=V_3(G),\qquad B=V_{\ge4}(G),\qquad b=|B|,\qquad
s=\sum_{v\in B}(d_G(v)-4).
\]

The paper proves

\[
\boxed{|A|\ge 2b+s+4},
\]

with the stated consequences

\[
3|A|\ge 2|V(G)|+s+4
\quad\text{and}\quad
|E(G)|\le 2|V(G)|-b-2.
\]

The separate \(b=1\) refinement and the \(b\ge2\) equality regimes are
claimed only in the exact forms proved in the manuscript.

## Read the preprint

- [Manuscript PDF](paper/manuscript.pdf)
- [Supplementary appendix PDF](paper/supplementary-appendix.pdf)
- [Manuscript and supplement sources](paper/source/)
- [Exact claim and nonclaim ledger](CLAIMS_AND_SCOPE.md)
- [Verification summary](VERIFICATION_SUMMARY.md)
- [Limitations](LIMITATIONS.md)

## Reproduce the finite checks

The written mathematical argument is the proof. The standard-library programs
are bounded falsification and regression instruments.

```sh
cd reproducibility
output_dir="$(mktemp -d)"
./RUN_ALL.sh "$output_dir"
```

Expected terminal prefix:

```text
PASS_EXACT_REPLAY_NO_SOURCE_MUTATION
```

The replay covers 343,980 admissible integer tuples, 33,866 labeled auxiliary
graphs, 281,197 exact branch-cycle lifts, both proved equality regimes, all
labeled cubic graphs on four and six vertices, and six deliberate mutations.
It uses two implementation-distinct programs and requires exact output-byte
agreement.

## Scope

- The global Erdős–Gyárfás conjecture is not solved.
- No two-port theorem or claim is imported.
- TP4–20 and CE22–26 are excluded.
- Finite computation corroborates but does not prove the theorem.
- Historical priority is not claimed absolutely; the recorded disposition is
  `NOVELTY_SUPPORTED_WITHIN_SCOPED_SEARCH`.
- External specialist review remains pending.

The legacy repository
[`ZackaryLoevseth/Erd-s-Problem-64`](https://github.com/ZackaryLoevseth/Erd-s-Problem-64)
preserves broader historical research. This clean repository is the candidate
canonical home for the paper and its narrowly scoped reproducibility material.

## Disclosure and reuse status

See [AI_USE_AND_AUTHOR_ROLE.md](AI_USE_AND_AUTHOR_ROLE.md) and
[LICENSE_STATUS.md](LICENSE_STATUS.md). No open-source or open-document reuse
license is granted by this release candidate.
