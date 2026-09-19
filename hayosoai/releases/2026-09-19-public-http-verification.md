# HayosoAi public starter — live HTTP verification

Checked September 19, 2026, at **17:18:37 UTC** (10:18:37 America/Los_Angeles).

## Result

The GitHub-hosted runner retrieved the public page with **HTTP 200** and confirmed that the returned HTML bytes exactly matched `docs/hayosoai/index.html` in the source revision below. This resolves the earlier launch note's outstanding HTTP-retrieval check for that revision.

- Public page: https://zackaryloevseth.github.io/research-portfolio/hayosoai/
- Source commit: `84cd09886944c79fabad23631f179ecd11ee1432`
- Response: `200`, `text/html; charset=utf-8`
- Returned bytes: `15959`
- Expected and observed SHA-256: `d18d47d7bc1d39fcfdf9c6bc72f06d4ea1bb3bab5e90b9caaecfe86eca98f217`
- Attempt: `1`
- Check timestamp: `2026-09-19T17:18:37.395859+00:00`

## Evidence and reproducibility

[Workflow run 35457680422](https://github.com/ZackaryLoevseth/research-portfolio/actions/runs/35457680422) completed successfully. Job `105935760587`, named `verify-public-pages`, contains the JSON result in the **Compare deployed public HTML with repository bytes** step and in the run summary.

[Exact checker source](https://github.com/ZackaryLoevseth/research-portfolio/blob/84cd09886944c79fabad23631f179ecd11ee1432/.github/workflows/hayosoai-public-smoke.yml).

The check makes GET requests only to this repository's public HayosoAi pages, compares SHA-256 values with the checked-out files, and has read-only repository permissions. It does not submit forms, contact third-party recipients, use private account data, or measure audience traffic. It runs on relevant changes or manual dispatch, not on a recurring schedule.

## Scope

This demonstrates successful retrieval and byte equality from the runner at the stated time. It is not an independent security audit, a guarantee of worldwide availability, an accessibility certification, a measurement of readership, or validation of the project's research or teaching materials. Later source changes or hosting conditions require a new check.

The Microsoft consultation and social-post publication are separate actions. This site check neither performs nor establishes either action.
