# Public site rollback

Release run: `PUBLIC-RELEASE-20260821T211555Z`

## Baseline and deployed state

- Initial public commit: `6794307b7e6093d932f2aa33f70ea9e40ef4314f`
- Frozen initial tag: `v1.0.0`
- Pages source: `main` from `/`
- Public URL: <https://zackaryloevseth.github.io/research-portfolio/>
- Public history: physically isolated; no private-control parent objects

## Rollback procedure

If a central-claim, privacy, security, or licensing defect is found:

1. Preserve an owner-only incident record and the exact affected commit.
2. Revert the defective correction with `git revert <defective-commit>` and
   push the resulting commit to `main`; do not force push or move `v1.0.0`.
3. If immediate containment is required, disable Pages while preserving the
   repository and all public Git history.
4. Correct through a new commit and versioned notice; do not rewrite ordinary
   scientific history.
5. Re-run the public/private diff and anonymous validation before redeployment.

The private deployment receipt records the exact live correction commit and
canonical revert command after the commit exists.
