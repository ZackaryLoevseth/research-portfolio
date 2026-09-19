# Offline shared-inquiry adapter

A small, standard-library Python exporter for inspecting the **existing fictional garden case** across plain notes, Discourse Graph data shapes, and W3C PROV-O. It makes no model calls and does not decide whether people should approve a proposal.

From this directory:

```sh
python3 -m unittest -v
python3 export_case.py case.json --source-dir sources --out my-new-export
```

The output directory must not exist; its parent must exist. Existing directories, including empty ones, are refused. No credentials, network service, account, plugin, or cloud sync is used. The input and original source files are preserved.

[`example-export-v1/`](example-export-v1/README.md) is an actual CLI export. Start with its [question](example-export-v1/notes/question.md); compare `notes/proposal-a.md` and `notes/proposal-b.md`, then their separate standing records. Their identical proposal text does not collapse the histories. The record also retains the objection, the participant's refusal to continue AI discussion, the assistant's proposal-only boundary, and insufficient information about trial bounds. None is empirical garden evidence.

## Export contents and limits

- `record.json`: every input field retained, including source references, exact excerpts, attribution, and partial coverage. This is the lossless interchange representation.
- `sources/*.md`: original byte-for-byte source copies verified against the input SHA256 values before output creation. The fixture uses the exact version 0.2 of [the shared case](../shared-inquiry-case-01.md), pinned to its source commit in `case.json`. Links inside the unmodified source copy remain relative to its original location; use the pinned source URL for that navigation.
- `notes/*.md`: ordinary readable Markdown with separate question, proposal, objection, stipulated-premise, and permission-record kinds. JSON-quoted scalar frontmatter supplies `nodeTypeId` and `nodeInstanceId`. IDs are stable UUIDv5 values, not invented actors or event identifiers.
- `relations.json`: version-1 file with ID-keyed relations, checked endpoint references, relation-type IDs, and the required record-creation metadata.
- `settings-fragment.json`: custom types and allowed relation triplets matching the inspected TypeScript shapes. It is **not** a complete plugin settings file or the plugin's schema-import format. Do not overwrite a real vault's settings with it.
- `provenance.ttl`: PROV entities for the authored records and source bytes; `wasDerivedFrom` describes derivation of a note from a document. It does not express support, consent, endorsement, or permission. No dates for fictional events are invented.
- `manifest.json`: SHA256 of all output files other than the manifest itself.

The mandatory numeric DG `created`/`modified` fields refer to the actual authored-record timestamp carried in the input, not the fictional garden chronology. Local relation instances omit sync fields and imported-record status. DG's imported/accepted UI terminology is not scientific acceptance or agreement in the case.

**Compatibility status:** source-inspected data-shape compatibility only. Obsidian UI loading, plugin schema import, discovery by filename format, rendering, cloud sharing, synchronization and cross-vault migrations are untested. No `.obsidian` directory or installation is generated. Use ordinary Markdown now; any actual plugin integration belongs in a disposable vault, with manual settings review and sync disabled, subject to the user's existing permissions. The exporter cannot enforce downstream plugin behavior.

The schema draft's empirical `Evidence` kind is deliberately not used for constructed case events. The custom kinds are a local extension, not a claim to standard semantic interoperability. If a receiving tool cannot retain them, keep the plain notes and record instead of silently relabeling them.

## Inspected sources

DiscourseGraphs/discourse-graph at commit [`51e2b924c195e8f9fd98138b1f2947496a82eb31`](https://github.com/DiscourseGraphs/discourse-graph/tree/51e2b924c195e8f9fd98138b1f2947496a82eb31): `apps/obsidian/src/types.ts`, `utils/relationsStore.ts`, `utils/discourseLinkFrontmatter.ts`, `utils/tldrawColors.ts`, and the sync/import guide. This is an original implementation from the observed format; no upstream implementation is vendored.

The [Discourse Graph conceptual schema](https://github.com/DiscourseGraphs/schemas/blob/main/conceptual-schema-draft.md) distinguishes empirical evidence from claims and permits local variations; it does not establish this adapter's fit. [W3C PROV-O](https://www.w3.org/TR/prov-o/) provides the provenance vocabulary, not an authority model.

## Checks performed

Ten unittest methods passed, including twelve malformed-record variants. They check lossless record/source preservation, identical proposals with distinct standing, retained objections, explicit incomplete scope, DG endpoint/type consistency, provenance separation, stable exports/manifests, duplicate IDs, unsafe paths, unknown attributes, source tampering, exact excerpts refusal to overwrite, and reader navigation through incoming relations and the complete note index. The integrated fixture has one source; the actual CLI wrote 17 files; an attempted repeat exited 2 without overwriting. An AI review found that outgoing-only links hid standing and objection records from readers; incoming links and a complete index now expose them, with a navigation regression. The first test run caught an apostrophe mismatch in a fixture excerpt; that excerpt was corrected to the source, not the source to the fixture.

These are software checks, not evidence that this representation improves model behavior, participation, consent, or institutional decisions. Source hashes authenticate matching bytes, not truth. Excerpt membership is not a semantic proof that a paraphrase is faithful. A human or other reader still needs to examine that mapping.

Independent Turtle parsing is recorded in [verification](VERIFICATION.md); actual plugin loading remains untested. No new rights or license are granted: the project's existing `LICENSE_STATUS.md` reserves rights and does not authorize outside copying, modification, or redistribution. Publication and technical inspectability do not resolve future adoption/reuse terms.
