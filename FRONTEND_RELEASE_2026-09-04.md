# Research-only frontend edition — 4 September 2026

This edition replaces the landing-page presentation and adds a printable research résumé. It does not replace scientific releases or their claim boundaries.

## Preserved source state

Base portfolio commit: `e9bc058fb5f8f6feb07e06006ca78e4a105da8a7`. Existing publication PDFs, evidence files, background pages, and Git history are preserved. No private reports, employer details, credentials, or new employment/proficiency claims are added.

## Changes

- Concise first-person landing page with four selected public results.
- Explicit separation of human direction, substantial AI assistance, and evidence.
- Keyboard-accessible five-step workflow explanation, with a no-JavaScript fallback. This is an explanation, not a live verification benchmark.
- Printable research-only résumé at `research-resume.html`.
- Working ETI hypothesis separated from demonstrated mathematics and unreported comparative efficacy.

## Local frontend checks

The HTML was rendered in Chromium at desktop and mobile widths. Tab selection, arrow-key navigation, no-JavaScript fallback, absence of horizontal overflow, and absence of JavaScript runtime errors were checked. The local browser could not access `file:` URLs under its policy, so the same HTML was loaded directly into a browser document for these checks. Remote link availability and GitHub Pages deployment are separate observations. No theorem checker was rerun.

## Manifests and history

`FRONTEND_SHA256_2026-09-04.json` covers only the listed changed files. Earlier root checksum files, asset manifests, status summaries, and deployment receipts remain historical for their original versions; they do not certify this frontend or the current whole tree. Scientific release manifests remain controlling for their frozen artifacts.

## Rollback

Restore the changed frontend paths from the recorded base commit through an ordinary reviewed revert. Do not force-push or delete scientific artifacts. The new résumé can remain historical or be removed only through an explicit repository change.

No new reuse license is granted.
