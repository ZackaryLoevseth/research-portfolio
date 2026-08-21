# Verification summary

Scientific package status: **PUBLICATION-READY PREPRINT — EXTERNAL SPECIALIST REVIEW PENDING**.

- Exact symbolic reconstruction checks the three unitriangular and two
  dihedral inequalities.
- The standard-library checker imports no producer module and recomputes all
  decisive integer comparisons.
- The C11 producer exhaustively enumerates all `2^21` elements of `U_7(2)`.
- The public middle census contains 744 rows for orders 129–255 and has a
  separate arithmetic checker.
- Nine unit and fault-injection tests reject decisive-field, truth-flag,
  schema, and integrity mutations.
- Optional GAP reconstruction is documented but is not required for the core
  release replay.
- The canonical frozen manuscript source-PDF SHA-256 is
  `aead9449a5096fc260c8d180360816a2ab709649ae50a48b4e3c84020ea346ea`.
- The public-release candidate PDF, changed only to reconcile data/code
  availability, has SHA-256
  `edc5c123ccdde18a7b8f971c7bf8f59d7b60135125f481c9596f494267517b3d`.

The public repackaging excludes one rejected malformed certificate and updates
only the frozen-file list and boundary test needed to enforce that exclusion.
The corrected v2 certificate, theorem arithmetic, producer code, expected
outputs, and paper bytes are unchanged. A clean-clone replay receipt is
recorded in `RELEASE_QA.md`.

These are method-diverse internal checks, not external peer review. The
Pak–Soffer class-number polynomial remains a cited dependency.
