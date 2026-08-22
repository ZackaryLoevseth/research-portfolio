# Verification summary

Current portfolio status: **PUBLIC GITHUB PREPRINT RELEASE — EXTERNAL
SPECIALIST REVIEW PENDING; NOT JOURNAL/ARXIV SUBMITTED**.

- The frozen package passed 21 of 21 scientific and publication gates.
- A definition-level proof reconstruction and hostile audit covered the branch
  graph, exact cycle lifting, 2-degeneracy, cut identities, parity, and the
  separate `b=0` and `b=1` cases.
- Two representation-distinct standard-library programs checked 343,980 exact
  integer tuples, 33,866 labeled auxiliary graphs, 281,197 branch-cycle lifts,
  all labeled cubic graphs at orders 4 and 6, a count-sharp control, and six
  deliberate mutations.
- The clean replay runs four unit tests, compares both complete output files
  byte for byte, verifies checksums before and after execution, and rejects any
  source-tree mutation.
- Frozen result-core SHA-256:
  `cdecbd8587daa494007e5e0f8acb23b5f6c34e0e9f0930da1fbc4a53c5b9b3f2`.
- Canonical frozen manuscript source-PDF SHA-256:
  `b71ca4ba5bda34c29b5abe11fc245233d63f20be61a4a1baccbdba22863f6f69`.
- Public-release manuscript PDF SHA-256:
  `fb781880e1d76a6b2fe1b78fe1646ac5e0b3b6a8d93714439c1a95a0607eb8cd`.
- Canonical frozen supplement source-PDF SHA-256:
  `4f9e361f117309c6770f521d835bcb15cc3e78f990703b0bb00da248baeffab9`.
- Public-release supplement PDF SHA-256:
  `5fce8824f153c9c048142b801e3f0baeb2044743eb0ad2d2065711a90de837af`.

The private prepublication tarball is deliberately excluded from this public
candidate because its embedded no-grant notice and release status are not the
public license for this repository. The independently identified first-party
verification files needed for replay are included individually and covered by
the public candidate's checksums.

These checks certify only their declared scopes. They are not a proof of the
global conjecture, absolute novelty, or external review.
