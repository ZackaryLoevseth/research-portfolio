# Publication completion preflight — 2026-09-07

The current prepared head was rechecked as `09cbb3a9c6e976c99c9117e734cedf47d835c6b6`, with base `397979806703b14caf721ecc980e63870f9fd667`. Its additional CI workflow is retained. All 11 source blobs pinned by the downloaded publication helper still match; the helper was inspected and its offline self-test passed. Its publishing mode was not used because it expects the earlier branch head.

The original foundations PDF is now included unchanged at `docs/assets/publications/eti/ETI_Foundations.pdf` (177843 bytes), and `docs/release.json` records the working manuscript. SHA-256: `e87a88c4dedbd9d53978d4bb90dbfe5186aacc007950dc5a8d87a5b2a31e2578`.

Both required commands passed in this complete checkout: all 13 correction-model tests and all publication-preflight checks. Existing résumé, mathematical PDFs, frozen release files, and unrelated work remain unchanged. These checks establish the publication candidate; successful CI, normal GitHub merge, Pages deployment, and live URL/browser checks are recorded separately when performed.

The original preparation record below is retained as history. Its PDF-transfer blocker is resolved by this completion; the branch now includes the publication CI workflow.

---

# Foundations-first portfolio update

Implementation branch: `portfolio-foundations-20260907`.
Base: `397979806703b14caf721ecc980e63870f9fd667`.

## Publication gate — do not merge before the PDF is present

The web source changes are committed, but the original user-supplied PDF has not yet been transferred into GitHub. The complete local handoff includes the unchanged PDF. The public site remains unchanged while this branch is in draft.

Required repository path:
`docs/assets/publications/eti/ETI_Foundations.pdf`

Required SHA-256:
`e87a88c4dedbd9d53978d4bb90dbfe5186aacc007950dc5a8d87a5b2a31e2578`

Required byte count: 177843. Version: ETI-SYNTHESIS-2026-09-07.1, 26 pages.

Before publication, upload that exact file to this branch and run from a complete checkout:

```sh
node --test tests/correction.test.cjs
node tests/portfolio-preflight.cjs
```

The preflight rejects an absent or altered PDF, missing local destinations and anchors on the four changed/new pages, and a mismatch between the embedded certificate and its pinned source. This is a manually run check, not a configured required GitHub status check. Do not merge a broken paper link. After merging, verify the actual Pages build and public URLs; neither a local test nor a branch commit is a deployment receipt.

## Changes

- The published `docs/` homepage now starts with Zackary Loevseth's research question and the foundational manuscript, with direct PDF and explanatory overview links.
- The old A-or-B checkbox example is replaced by a two-history comparison that computes grounded closure, exact reopening patches, saved-information cells and common-correction conflicts. It distinguishes updating the withdrawal record from reopening a claim, and explicitly allows retrieval as additional information.
- Four mathematical outputs remain distinct from the ETI program.
- A trajectory explorer embeds the exact published F104 CSV and exposes all 105 integer states, factorizations and 104 transitions with native keyboard controls and a labeled logarithmic plot.
- The foundations overview includes the manuscript's exact tie-policy example, source-page links, contribution statement and evidence boundaries.
- The papers page puts the synthesis first while preserving existing release, manuscript, supplement and attribution links. The separate finite-note package retains its separate release status.
- A dedicated stylesheet preserves the cream/green/serif direction without changing other pages' existing stylesheet. New pages are included in the sitemap.

The approved resume, existing mathematical PDF bytes, old root homepage, frozen release manifests and historical deployment receipts were not overwritten.

## Checks actually performed locally

- 13 Node correction-model tests passed.
- Four pages rendered at 1440, 768, 390 and 320 CSS-pixel widths: no horizontal document overflow or JavaScript errors in these checks.
- Correction event, both saved-record modes, reset, native radio keyboard navigation and button activation checked.
- Trajectory endpoint, previous-step and native range Home/End controls checked.
- All 105 certificate rows checked with exact-integer factor products, primality checks, totient values and consecutive transitions; the first prime is at index 104.
- The CSV matches Git blob `d8d3c17f12b0b0264a26b22d791c696dca54764b` from pinned commit `ee62d68d16f187b808c814108fd53881c4e3e614` in the certificate repository.
- The local PDF copy matches the user upload byte for byte.

Browser rendering used Chromium with local HTML/CSS/JavaScript supplied through `set_content` because this runtime blocked local URL navigation. This does not substitute for deployed URL testing. The full-checkout link/PDF preflight remains a publication obligation. No historical ETI benchmark suite, external review or comparative model-performance study was replayed or inferred from these website tests.
