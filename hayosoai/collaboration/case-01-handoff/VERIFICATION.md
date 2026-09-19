# Verification and compatibility limits

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

The destination must not already exist. A repeated invocation to an existing destination is expected to fail with exit 2. Compare generated files with `example-export-v1/`; identical input produces identical output bytes.

Optional independent Turtle check in an environment where RDFLib 7.1.4 is already installed:

```sh
python3 -c 'from rdflib import Graph; g=Graph().parse("example-export-v1/provenance.ttl", format="turtle"); print(len(g))'
```

Expected output: `53`. Parsing checks RDF syntax, not the adequacy of the record or the validity of its propositions.

## Not tested or established

No actual Obsidian plugin loading, schema import, cloud sync, cross-vault migration or downstream enforcement was performed. `settings-fragment.json` is a mapping aid, not an installable configuration. No participant activity, external adoption, independent human review, ecological benefit or improvement in model behavior is established. The existing Reopening Probe and Pilot 01 were not changed or rerun.

The ordinary prose case remains an alternative: a more elaborate record is useful only if it helps a receiving person or process without displacing their judgment or adding unjustified burdens. Existing licensing remains unchanged.
