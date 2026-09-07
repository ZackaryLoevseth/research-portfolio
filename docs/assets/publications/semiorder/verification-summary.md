# Verification summary

Current portfolio status: **PUBLIC GITHUB PREPRINT RELEASE — EXTERNAL SPECIALIST REVIEW PENDING; NOT JOURNAL/ARXIV SUBMITTED**.

- The computation-independent geometric proof is separated from the finite
  checker and from the unrestricted research campaign.
- The unchanged standard-library checker covers 318,667 cases, 3,978,057
  ideals, and 2,311,018 distinct projected points.
- Checker SHA-256:
  `b68e3ef7a43c23b29ba2a8ea8883b7d4488f666315d25cbf10ddc7eb1fd17e96`.
- Result-core SHA-256:
  `2f5da66840fb3a837d022ec1a48499b24df659dc6cefdb82c2166e62517891e8`.
- The package retains the authoritative V2 replay driver, four tests, exact
  expected output, proof record, internal audit, and source-provenance record.
- The zero-mutation wrapper hashes all repository files before and after the
  exact replay. The mutation harness alters only disposable copies and requires
  checker-hash, expected-count, and missing-contract mutations to fail.

A clean-clone replay receipt is recorded in `RELEASE_QA.md`. The verifier is
method-distinct internal evidence, not external peer review or a proof
assistant.
