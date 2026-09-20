# Verification and compatibility limits

## Edition 2 — September 20, 2026

The current files at the preserved `example-export-v1/` URL are **handoff edition 2**, derived from English case 0.3. The path is retained for existing readers; it does not claim byte identity with edition 1. The original export and its receipt below remain historical.

Python 3.12.14: **11 unittest methods passed**, including a new regression requiring the receiving note to retain the unassigned response responsibility, missing accessible route, and unresolved decision. The actual CLI produced 17 files; all 16 listed output hashes and the exact source copy were checked. RDFLib 7.1.4 separately parsed the current Turtle output as 53 triples. No new schema or permission enforcement was introduced.

Source SHA-256: `e1a3a1e26ead66647888fac30b7041bf745517230cecc94d11cba2c099e2d360`. The Spanish 0.3 preview records its matching English version and remains AI-generated without competent human translation or local pedagogical review.

An anonymous GitHub Markdown walkthrough of edition 1 reached question → proposal → standing and objection → nonparticipation through the rendered links. That establishes inspectable navigation in that receiving surface, not plugin import or effective contestability. The walkthrough exposed the response-responsibility omission corrected in edition 2.

## Historical edition 1 check

Checked September 19, 2026 with Python 3.12.14. This is software verification of an offline exporter, not a model trial or evaluation of a decision process.

- `python3 -m unittest -v`: **10 test methods passed**, including twelve malformed-record variants. Tests cover exact sources/excerpts, complete record retention, stable exports, separate proposal/permission histories, unknown scope, type/endpoints, source tampering, unsafe paths and refusal to overwrite.
- Actual CLI invocation produced **17 files** with ten notes and nine semantic relations. `manifest.json` records all other output hashes.
- A reader can follow the question to both proposals, then to their objections and standing records. Every note, including the unconnected water-estimate premise, is listed in the export index. This was added after an AI review found outgoing-only links hid relevant context.
- A separate RDF parser, **RDFLib 7.1.4**, accepted `provenance.ttl`: **53 triples, 11 entities, 10 derivation edges**, each ending at the exact source-byte entity. The parser was installed outside this project for verification; it is not an exporter dependency.
- Exact English case source SHA-256: `71b2f950a1370269869d3cd724054b64bc6916e811315dd8a4353b2ded41cbee`. The byte-identical source copy and machine-checked excerpts preserve provenance, not a proof of paraphrase meaning or truth.

## Reproduce locally

From this directory, with Python available:

```sh
python3 -m unittest -v
python3 export_case.py case.json --source-dir sources --out my-new-export
```

The destination must not already exist. A repeated invocation to an existing destination is expected to fail with exit 2. For the current edition, compare generated files with `example-export-v1/`; identical current input produces identical output bytes. Historical edition 1 used its then-current source and record.

Optional independent Turtle check in an environment where RDFLib 7.1.4 is already installed:

```sh
python3 -c 'from rdflib import Graph; g=Graph().parse("example-export-v1/provenance.ttl", format="turtle"); print(len(g))'
```

Expected output: `53`. Parsing checks RDF syntax, not the adequacy of the record or the validity of its propositions.

## Not tested or established

No actual Obsidian plugin loading, schema import, cloud sync, cross-vault migration or downstream enforcement was performed. `settings-fragment.json` is a mapping aid, not an installable configuration. No participant activity, external adoption, independent human review, ecological benefit or improvement in model behavior is established. The existing Reopening Probe and Pilot 01 were not changed or rerun.

The ordinary prose case remains an alternative: a more elaborate record is useful only if it helps a receiving person or process without displacing their judgment or adding unjustified burdens. Existing licensing remains unchanged.
