# Replay report

Date: 2026-08-18  
Package: `G3_FIVE_FINITE_GROUP_REFUTATIONS_V1`  
Working-directory policy: package-relative commands; generated build/results in
an automatically removed temporary directory.

## Core replay

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/replay.py
```

Result: `PASS` (exit 0).

The replay completed:

- standard-library independent checker: PASS;
- nine unit and fault-injection tests: PASS;
- retained family-proof checker: PASS;
- distinct arithmetic audit of all 744 middle-census rows: PASS;
- C11 `U_4(2)` self-test: PASS;
- exhaustive one-thread enumeration of all `2^21` `U_7(2)` elements with
  cross-checked ranks: PASS;
- fresh C result versus sealed certificate, excluding elapsed time and selected
  thread count: exact agreement;
- copied immutable-asset, producer-input, and certificate-output SHA-256
  manifests: PASS.

The independent checker returned exact witness slacks `-5,053,212` (C20),
`-31,275` (C21), `-31,331` (C22), `-52` after C27 scaling, and `23,640,000`
in the C28 fifth-power comparison. The middle census contained 744 rows, 92
p-groups, ten C20 failures first appearing at order 243, and no C22 failure.

## Fault-injection scope

Tests reject:

- a mutated and correctly resealed `U_7(2)` class number;
- a changed decisive dihedral class number;
- a flipped middle-census truth flag;
- an immutable asset hash mismatch;
- malformed or bundled external-input records;
- a malformed external archive-checksum sidecar when that sidecar is present;
  its absence inside the archive is intentional and archive-aware;
- a mutated decisive field in the corrected GAP invariant table; and
- a synthetic middle-census row whose negative C20 linear side must be treated
  as a failure even when its squared slack is nonnegative.

## GAP replay

Status: `PASS` (exit 0; observed total wall time 4.83 seconds, including core
replay).

The replay used an isolated GAP 4.16.0 executable (SHA-256
`a617dba573cc5f51bf53db4e0eaa5e497df038801c368d44a4b6996a4f7c85ea`)
with SmallGrp 1.5.5. It reconstructed and byte-compared the dihedral,
order-243, `U_7(2)` pc-presentation, and 129--255 census artifacts. Every GAP
script ran under `--bare -q -b` and emitted its required success sentinel.

An earlier ambient-initialization attempt was rejected: a missing optional
package caused GAP to enter a break loop while returning process status zero.
That defect led to the sentinel requirement and is preserved in
`CORRECTIONS.md`.

## Cleanliness

No compiled binary, temporary result, external census, source PDF, or Python
`__pycache__` directory remains in the package. No public upload, repository
publication, or external message was used during the replay.
