# Public site rollback

Release run: `PUBLIC-RELEASE-20260821T211555Z`

## Before deployment

- Previous public repository: not yet confirmed with full-account visibility
- Previous Pages state: public URL returned 404 during preflight
- Candidate history: physically isolated; no private-control parent objects

## Rollback procedure

If a central-claim, privacy, security, or licensing defect is found:

1. Disable Pages in **Settings → Pages** or select `None` as the source.
2. Make the repository private if immediate containment is required.
3. Preserve an owner-only incident record and the exact affected commit.
4. Correct through a new commit and versioned notice; do not rewrite ordinary
   scientific history.
5. Re-run the public/private diff and anonymous validation before redeployment.

The final deployment receipt must append the previous commit, deployed commit,
source branch, Pages state, affected URLs, and exact revert command.
