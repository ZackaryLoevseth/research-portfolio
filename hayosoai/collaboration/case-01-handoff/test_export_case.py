import copy
import json
import pathlib
import shutil
import tempfile
import unittest

import export_case as adapter

HERE = pathlib.Path(__file__).parent


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((HERE / "case.json").read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.source = self.root / "sources"
        shutil.copytree(HERE / "sources", self.source)

    def run_export(self, name="export", record=None):
        out = self.root / name
        adapter.export(self.record if record is None else record, self.source, out)
        return out

    def test_lossless_record_sources_and_objection_survive(self):
        out = self.run_export()
        self.assertEqual(json.loads((out / "record.json").read_text()), self.record)
        for source in self.record["sources"]:
            self.assertEqual((out / "sources" / source["file"]).read_bytes(), (self.source / source["file"]).read_bytes())
        for node in self.record["nodes"]:
            note = (out / "notes" / (node["id"] + ".md")).read_text()
            self.assertIn(node["text"], note)
            self.assertIn(self.record["attribution"], note)
        self.assertIn("Refusal is not consent", (out / "notes/nonparticipation.md").read_text())

    def test_receiving_note_preserves_unassigned_response_without_inventing_permission(self):
        out = self.run_export()
        note = (out / "notes/nonparticipation.md").read_text()
        self.assertIn("does not identify who is responsible for responding", note)
        self.assertIn("or an accessible response route", note)
        self.assertIn("does not settle whether the trial should proceed", note)
        self.assertNotIn("Permission status", note)

    def test_same_proposal_different_standing_and_unknown_scope(self):
        out = self.run_export()
        nodes = {n["id"]: n for n in json.loads((out / "record.json").read_text())["nodes"]}
        self.assertEqual(nodes["proposal-a"]["text"], nodes["proposal-b"]["text"])
        self.assertEqual(nodes["standing-a"]["permission"]["status"], "not-authorized")
        self.assertEqual(nodes["standing-b"]["permission"]["agreement"], "dissent-retained")
        self.assertEqual(nodes["trial-scope-unknown"]["permission"]["status"], "insufficient-record")
        self.assertNotIn("permission", nodes["nonparticipation"])

    def test_reader_can_find_standing_and_objections_from_question(self):
        out = self.run_export()
        index = (out / "README.md").read_text()
        for node in self.record["nodes"]:
            self.assertIn(f"](notes/{node['id']}.md)", index)
        question = (out / "notes/question.md").read_text()
        for history in ("a", "b"):
            self.assertIn(f"](proposal-{history}.md)", question)
            proposal = (out / f"notes/proposal-{history}.md").read_text()
            self.assertIn(f"](standing-{history}.md)", proposal)
            self.assertIn("](food-objection.md)", proposal)
            self.assertIn("Incoming recorded relations", proposal)
        b = (out / "notes/proposal-b.md").read_text()
        self.assertIn("](trial-scope-unknown.md)", b)
        self.assertIn("](assistant-boundary.md)", b)
        objection = (out / "notes/food-objection.md").read_text()
        self.assertIn("](nonparticipation.md)", objection)

    def test_dg_endpoints_and_custom_types_are_representable(self):
        out = self.run_export()
        frontmatter = [dict(line.split(": ", 1) for line in p.read_text().split("---\n")[1].strip().splitlines()) for p in (out / "notes").glob("*.md")]
        ids = {json.loads(f["nodeInstanceId"]) for f in frontmatter}
        schema = json.loads((out / "settings-fragment.json").read_text())
        types = {t["id"] for t in schema["relationTypes"]}
        kinds = {t["id"] for t in schema["nodeTypes"]}
        self.assertTrue(all(json.loads(f["nodeTypeId"]) in kinds for f in frontmatter))
        relations = json.loads((out / "relations.json").read_text())["relations"]
        for key, relation in relations.items():
            self.assertEqual(key, relation["id"])
            self.assertTrue({relation["source"], relation["destination"]} <= ids)
            self.assertIn(relation["type"], types)
            self.assertNotIn("status", relation)  # No accepted/verified claim inference.
        self.assertFalse(any(t["name"] == "Evidence" for t in schema["nodeTypes"]))

    def test_derivation_is_separate_from_semantic_relations(self):
        out = self.run_export()
        ttl = (out / "provenance.ttl").read_text()
        self.assertEqual(ttl.count("prov:wasDerivedFrom"), len(self.record["nodes"]))
        self.assertNotIn("prov:wasAttributedTo", ttl)
        self.assertNotIn("prov:startedAtTime", ttl)
        self.assertNotIn("records-standing", ttl)
        self.assertIn("dct:type \"permission-record\"", ttl)

    def test_reproducible_export_and_manifest(self):
        a, b = self.run_export("a"), self.run_export("b")
        files = lambda p: {str(f.relative_to(p)): f.read_bytes() for f in p.rglob("*") if f.is_file()}
        self.assertEqual(files(a), files(b))
        for path, sha in json.loads((a / "manifest.json").read_text())["files"].items():
            self.assertEqual(adapter.digest((a / path).read_bytes()), sha)

    def test_no_overwrite_even_empty_directory_or_symlink(self):
        existing = self.root / "export"
        existing.mkdir()
        with self.assertRaises(ValueError): self.run_export()
        link = self.root / "link"
        link.symlink_to(self.root / "absent")
        with self.assertRaises(ValueError): adapter.export(self.record, self.source, link)
        self.assertEqual(list(existing.iterdir()), [])

    def test_source_identity_and_excerpt_required(self):
        (self.source / "case.md").write_bytes(b"changed source")
        with self.assertRaisesRegex(ValueError, "hash mismatch"): self.run_export()
        shutil.copy(HERE / "sources/case.md", self.source / "case.md")
        self.record["nodes"][0]["excerpt"] = "invented source passage"
        with self.assertRaisesRegex(ValueError, "excerpt not found"): self.run_export()

    def test_refuses_unknown_fields_kinds_missing_endpoints_and_conflation(self):
        mutations = [lambda r: r.update(approved=True),
                     lambda r: r["nodes"][0].update(kind="Evidence"),
                     lambda r: r["nodes"][0].update(permission={}),
                     lambda r: r["nodes"][0].update(source="missing"),
                     lambda r: r["relations"][0].update(destination="missing"),
                     lambda r: r["relations"][0].update(type="authorizes"),
                     lambda r: r["relations"][0].update(type="records-standing"),
                     lambda r: r["relations"][4].update(destination="proposal-b"),
                     lambda r: r.update(coverage="complete"),
                     lambda r: r["nodes"][5]["permission"].update(agreement="consent-inferred"),
                     lambda r: r["nodes"].append(copy.deepcopy(r["nodes"][0])),
                     lambda r: r["relations"][0].update(approved=True)]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                record = copy.deepcopy(self.record)
                mutate(record)
                with self.assertRaises(ValueError): self.run_export(record=record)
                self.assertFalse((self.root / "export").exists())

    def test_path_traversal_and_source_symlinks_rejected(self):
        self.record["nodes"][0]["id"] = "../../escape"
        with self.assertRaises(ValueError): self.run_export()
        self.record["nodes"][0]["id"] = "question"
        with self.assertRaises(ValueError): adapter.export(self.record, self.source, self.root / ".." / "escape")
        self.record["sources"][0]["file"] = "../../case.md"
        with self.assertRaises(ValueError): self.run_export()
        self.record["sources"][0]["file"] = "case.md"
        (self.source / "case.md").unlink()
        (self.source / "case.md").symlink_to(HERE / "sources/case.md")
        with self.assertRaises(ValueError): self.run_export()


if __name__ == "__main__":
    unittest.main()
