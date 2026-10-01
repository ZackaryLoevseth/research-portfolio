# Portfolio maintenance

The site lives in `docs/` and uses the built-in GitHub Pages branch publishing route. `SITE_DEPLOYMENT_ALLOWLIST.json` binds the exact public site files. Original scientific PDFs, evidence assets and frozen releases remain unchanged. Historical root-level site files and old manifests are preserved as history; `docs/` is the current presentation source.

Four mathematical releases are public. The finite ETI note and reference implementation remain under separate attribution and license review. The Study 14 comparison has no established comparative results. Public release, independent specialist review and journal publication are distinct statuses.

Human direction and substantial AI assistance are described on the Methods page and in project-specific contribution panels. No new reuse license is granted by this presentation change.

## Updating the published security record

Add an entry to `content/security-disclosures.json` only after a public advisory is available. Verify the identifier, publication date, publisher, and remediation metadata against that record. Update `verified_on` after checking the listed records. Product/CVE headings avoid carrying a technical title under revision into the portfolio.

Run `node scripts/build-security.mjs` to update the disclosure sections in the maintained homepage and security page. The build rejects entries whose status is not `published`. Keep confidential reports and unpublished candidates out of the source and presentation.

Before publishing, run:

```sh
node --test tests/correction.test.cjs
node tests/portfolio-preflight.cjs
node scripts/build-security.mjs --check
```

The beta generator is not included in this checkout. Its generated pages remain unchanged by the portfolio integration; future beta changes still require its maintained source project, as directed by `AGENTS.md`.
