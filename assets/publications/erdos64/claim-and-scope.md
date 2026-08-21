# Claims and scope

## Exact central theorem

Assume the Erdős–Gyárfás conjecture has a counterexample, and choose one
lexicographically by minimum order and then minimum size. With

```text
A = degree-three vertices
B = vertices of degree at least four
b = |B|
s = sum over v in B of (d(v)-4)
```

the manuscript proves

```text
|A| >= 2b+s+4
3|A| >= 2|V|+s+4
|E| <= 2|V|-b-2
```

For `b=1`, it also proves

```text
|A| >= 8+2s+(s mod 2)
|E| <= 2|V|-4-ceil(s/2).
```

For `b>=2`, equality in the central inequality holds exactly in the two
regimes stated in Remark 6 of the manuscript.

## Exact nonclaims

- The global Erdős–Gyárfás conjecture remains open.
- The theorem neither constructs nor rules out a counterexample.
- It does not prove that the high-degree set is empty, or that a minimal
  counterexample is cubic or 3-connected.
- No two-port, multipole, terminal-path-spectrum, TP4–20, CE22–26, or
  finite-SAT claim is imported.
- The 16-vertex equality control is sharp only for the local counting
  ingredients; it contains dyadic cycles and is not a counterexample.
- Finite computation corroborates the argument but is not the general proof.
- `NOVELTY_SUPPORTED_WITHIN_SCOPED_SEARCH` does not establish absolute
  novelty, priority, or a world-first result.
- No external specialist or peer review has occurred.
