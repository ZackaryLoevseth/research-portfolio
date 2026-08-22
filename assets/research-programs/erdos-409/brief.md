# Erdős Problem #409 — Current F=104 Pointwise Certificate

**Status: PUBLIC POINTWISE CERTIFICATE `F(400000287233629)=104`; GLOBAL PROBLEM OPEN**

## Research question

For the iteration `T(n)=φ(n)+1`, how large can the stopping time `F(n)` be before the trajectory reaches a prime? Erdős Problem #409 also asks whether infinitely many starting values can reach a common terminal prime and what density such basins have. The program separates finite pointwise records from those global questions.

## Contribution and current result

The current public release establishes the pointwise result

`F(400000287233629)=104`,

with the consequence `sup_n F(n) >= 104`. The released certificate is scoped
to this exact finite trajectory. It does not claim world-record priority,
unboundedness, global maximality, basin infinitude, density, inverse-tree
completeness, or a solution of the global problem.

The earlier public `F=71` baseline certified the chain

`F(6,148,888,817)=68`, `F(6,152,490,577)=69`, `F(6,665,198,137)=70`, and `F(6,668,696,999)=71`,

all terminating at the prime `9,500,401`. The package contains the 72-node `F=71` trajectory, exact factorizations, 222 recursive Lucas/Pratt-style primality certificates, and an independently reconstructed inverse-totient tree rooted at the `F=68` witness. Its exact level counts are `1, 10, 42, 10, 0` through the direct `F=72` extension level, with 62 parent–child edges.

The adjacent `brief.pdf` is an archived, explicitly historical `F=71`-only
snapshot. It is **not** the current program brief and is superseded for current
pointwise-certificate status by this document, release `v3.0.0-f104`, and
commit `ee62d68d16f187b808c814108fd53881c4e3e614`.

## Methods

The public release combines exact totient transitions, a canonical trajectory,
factorization data, package-free verification, a distinct SymPy verifier, an
independent Pollard–Rho/Miller–Rabin audit, mutation rejection, integrity
manifests, and continuous integration. These checks establish only the stated
pointwise certificate and its direct supremum consequence.

## Zackary’s role

The public record identifies Zackary as research director: he selected and preserved the target, designed the search and certification protocol, required independent reimplementation and explicit claim boundaries, directed recovery and repository restructuring, and approved the public scope. Final authorship, affiliation, and record-priority attestations remain human-controlled.

## AI and tool role

OpenAI and Anthropic systems substantially assisted with forward and inverse search strategy, algorithm and code generation, exact computation, certificate construction, independent reimplementation, recovery, and drafting. Python, SymPy, GitHub Actions, CSV/JSON data, and SHA-256 manifests make the resulting claims inspectable. AI assistance is disclosed and does not replace external review.

## Verification

At public head commit [`ee62d68d16f187b808c814108fd53881c4e3e614`](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/commit/ee62d68d16f187b808c814108fd53881c4e3e614), the prepared frozen release gates passed. Fresh replay by the SymPy verifier, dependency-free verifier, and independent Pollard–Rho/Miller–Rabin audit agreed on `F=104`, terminal prime `27515203921`, and the trajectory hash; all six required mutations were rejected.

## Exact nonclaims

The project does not solve Erdős Problem #409. The public result is limited to
`F(400000287233629)=104` and `sup_n F(n) >= 104`. It establishes no world-record
priority, global upper bound or maximum, unboundedness, basin infinitude,
density theorem, inverse-tree completeness, or global solution.

## Public artifacts

- [Public repository](https://github.com/ZackaryLoevseth/Erd-s-Problem-409)
- [F=104 release](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/releases/tag/v3.0.0-f104)
- [F=104 verification code and data](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/tree/ee62d68d16f187b808c814108fd53881c4e3e614)
- [Historical F=71 commit](https://github.com/ZackaryLoevseth/Erd-s-Problem-409/tree/995545f3ab2cfb3c1cb971f8d473140c4108eb6f)
- Archived local PDF: `brief.pdf` — historical F=71-only snapshot, superseded
  for current status

## Employer relevance

This is the clearest public example of exact computational research in the portfolio: certificate design, deterministic data generation, multiple verification paths, recovery discipline, CI, and calibrated claims. It is directly relevant to research engineering, computational mathematics, verification, data integrity, and reproducible scientific software.
