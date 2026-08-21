# Erdős Problem #409 — Certified Records and Inverse-Totient Research

**Status: CERTIFIED COMPUTATIONAL RECORDS THROUGH `F=71` / ACTIVE RESEARCH — TARGET OPEN**

## Research question

For the iteration `T(n)=φ(n)+1`, how large can the stopping time `F(n)` be before the trajectory reaches a prime? Erdős Problem #409 also asks whether infinitely many starting values can reach a common terminal prime and what density such basins have. The program separates finite pointwise records from those global questions.

## Contribution and current result

The strongest currently public result is the certified chain

`F(6,148,888,817)=68`, `F(6,152,490,577)=69`, `F(6,665,198,137)=70`, and `F(6,668,696,999)=71`,

all terminating at the prime `9,500,401`. The package contains the 72-node `F=71` trajectory, exact factorizations, 222 recursive Lucas/Pratt-style primality certificates, and an independently reconstructed inverse-totient tree rooted at the `F=68` witness. Its exact level counts are `1, 10, 42, 10, 0` through the direct `F=72` extension level, with 62 parent–child edges.

An internal `F=104` packet is a selected continuation target, not a promoted public result. The current director checkpoint requires a fresh independent replay, inverse-fiber reconstruction, bounded-search accounting, and a current record-priority audit before it can supersede the public `F=71` state.

## Methods

The public archive combines deterministic packet generation, exact totient transitions, compressed certificate data, flat CSV tables, package-free verification, a separate factor-from-scratch implementation, a compact SymPy check, integrity manifests, and continuous integration. The inverse route exhaustively solves the declared rooted predecessor problem while preserving the distinction between local exhaustion and global nonexistence.

## Zackary’s role

The public record identifies Zackary as research director: he selected and preserved the target, designed the search and certification protocol, required independent reimplementation and explicit claim boundaries, directed recovery and repository restructuring, and approved the public scope. Final authorship, affiliation, and record-priority attestations remain human-controlled.

## AI and tool role

OpenAI and Anthropic systems substantially assisted with forward and inverse search strategy, algorithm and code generation, exact computation, certificate construction, independent reimplementation, recovery, and drafting. Python, SymPy, GitHub Actions, CSV/JSON data, and SHA-256 manifests make the resulting claims inspectable. AI assistance is disclosed and does not replace external review.

## Verification

At public head commit [`995545f3ab2cfb3c1cb971f8d473140c4108eb6f`](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/commit/995545f3ab2cfb3c1cb971f8d473140c4108eb6f), CI passed. A clean local replay independently verified all 18 manifest entries, `F(6,668,696,999)=71`, the terminal prime, all 222 prime certificates, the inverse-tree counts, and the independent output `71 9500401`.

## Exact nonclaims

The project does not solve Erdős Problem #409. It establishes no global upper bound or maximum, no nonexistence of `F≥72`, no infinitude of a terminal-prime basin, and no density theorem. The empty direct `F=72` level is local to one rooted inverse tree. The repository does not claim that `71` is the current world record without a fresh literature comparison, and the internal `F=104` packet is not yet the current public record.

## Public artifacts

- [Public repository](https://github.com/ZackaryLoevseth/Erd-s-Problem-409)
- [Commit-pinned research status](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/blob/995545f3ab2cfb3c1cb971f8d473140c4108eb6f/RESEARCH_STATUS.md)
- [Verification code and data](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/tree/995545f3ab2cfb3c1cb971f8d473140c4108eb6f)

## Employer relevance

This is the clearest public example of exact computational research in the portfolio: certificate design, deterministic data generation, multiple verification paths, recovery discipline, CI, and calibrated claims. It is directly relevant to research engineering, computational mathematics, verification, data integrity, and reproducible scientific software.
