# Replay report

Publication ID: `PC_SEMIORDER_ZONOTOPE_BOUNDS_V1`  
Director run: `ASD-20260819T060116Z`

The decisive checker was replayed from a clean worktree reconstructed from the
preserved Git bundle at commit
`f9f0edf1d853a6de7b3c1e7a70076748a49a52bc`, after a ten-object source gate.

Command:

```sh
python3 -B src/verify_semiorder_geometric_bound.py
```

Result:

- status: `PASS`;
- exact cases: `318667`;
- ideals enumerated: `3978057`;
- distinct projected points: `2311018`;
- checker SHA-256:
  `b68e3ef7a43c23b29ba2a8ea8883b7d4488f666315d25cbf10ddc7eb1fd17e96`;
- result-core SHA-256:
  `2f5da66840fb3a837d022ec1a48499b24df659dc6cefdb82c2166e62517891e8`;
- wall time: `47.12` seconds;
- peak resident memory: `23085056` bytes;
- network and nonstandard packages: none.

The package replay driver additionally freezes the checker bytes, parses exact
JSON, and rejects schema, count, or digest mismatch. Final clean-archive replay
is recorded in the director verification directory so that this frozen
reproducibility archive does not become self-referential.

The first archive-QA attempt exposed that invoking the unchanged checker
without an explicit `--output` creates a new result file inside the package.
Although that file matched the frozen expected result byte-for-byte, it
violated the no-unexpected-mutation gate. Replay driver V2 therefore directs
the checker's declared file output to a temporary directory, verifies that it
matches stdout and the full frozen expected JSON, and then removes the
temporary directory. The rejected V1 archive is retained outside this package.

This is finite internal falsification evidence. It is not the theorem proof,
external specialist review, or proof-assistant verification.
