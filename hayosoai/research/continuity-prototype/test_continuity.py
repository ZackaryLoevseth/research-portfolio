import ast
import copy
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import continuity as c
from fixtures import ax, event, observation, path_get, resolve, scenarios, t

HERE = Path(__file__).resolve().parent


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / "events.jsonl"

    def install(self, events):
        for e in events:
            c.append(self.log, e)
        return c.view(self.log, events[-1]["recorded_at"])

    def assert_rejected_unchanged(self, e, expected_id=None):
        before = self.log.read_bytes() if self.log.exists() else b""
        with self.assertRaises((ValueError, TypeError)):
            c.append(self.log, e, expected_id)
        self.assertEqual(self.log.read_bytes() if self.log.exists() else b"", before)

    def test_required_scenarios_at_every_checkpoint(self):
        for scenario in scenarios():
            rows = resolve(scenario["events"])
            c.records_from_events(rows)
            for check in scenario["checks"]:
                end = next(n for n, e in enumerate(rows) if e["key"] == check["after"]) + 1
                v = c.project(rows[:end], check["at"])
                for path, expected in check["facts"].items():
                    with self.subTest(scenario=scenario["name"], checkpoint=check["after"], path=path):
                        self.assertEqual(path_get(v, path), expected)

    def test_exact_retry_idempotent_even_after_later_events(self):
        first = observation("a", "workflow", "draft", 1)
        self.install([first, observation("b", "workflow", "submitted", 2)])
        before = self.log.read_bytes()
        self.assertEqual(c.append(self.log, first), (c.digest(first), False))
        self.assertEqual(self.log.read_bytes(), before)

    def test_reused_command_key_and_claimed_event_id_rejected_atomically(self):
        first = observation("a", "validity", "valid", 1)
        self.install([first])
        changed = copy.deepcopy(first)
        changed["data"]["value"] = "invalid"
        self.assert_rejected_unchanged(changed)
        changed["key"] = "b"
        self.assert_rejected_unchanged(changed, c.digest(first))

    def test_python_equal_numeric_types_do_not_bypass_replay_identity(self):
        first = observation("a", "validity", "valid", 1)
        self.install([first])
        for version in (True, 1.0):
            changed = copy.deepcopy(first)
            changed["version"] = version
            self.assertEqual(changed, first)  # Python equality is weaker than JSON identity.
            self.assert_rejected_unchanged(changed)

    def test_malformed_event_variants_rejected_without_writes(self):
        self.install([observation("a", "validity", "valid", 1)])
        base = observation("b", "validity", "valid", 2)
        variants = [
            {**base, "approved": True}, {**base, "version": True},
            {**base, "kind": "approval"}, {**base, "actor_claim": {"role": "human"}},
            {**base, "depends_on": ["missing"]}, {**base, "recorded_at": t(0)},
            {**base, "recorded_at": "2026-02-30T00:00:00Z"},
            {**base, "data": {**base["data"], "axis": "paid_and_accepted"}},
            {**base, "data": {**base["data"], "value": "submitted"}},
            {**base, "data": {**base["data"], "observed_at": t(3)}},
            {**base, "data": {**base["data"], "valid_until": t(2)}},
            {**base, "data": {**base["data"], "evidence_ref": "/private/report.txt"}},
            {**base, "data": {**base["data"], "verified_human": True}},
            {"key": "broken"}, [], None,
        ]
        for bad in variants:
            with self.subTest(bad=bad):
                self.assert_rejected_unchanged(bad)

    def test_duplicate_json_keys_nonfinite_blank_and_partial_records_rejected(self):
        for raw in [b'{"seq":1,"seq":2}\n', b'{"x":NaN}\n', b"\n", b'{"unfinished":true}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                c.decode_log(raw)

    def test_record_tampering_reordering_deletion_and_duplication_detected(self):
        self.install([observation("a", "workflow", "draft", 1),
                      observation("b", "workflow", "submitted", 2)])
        records = c.load(self.log)
        bad = copy.deepcopy(records)
        bad[0]["event"]["data"]["value"] = "closed"
        for rows in [bad, list(reversed(records)), records[1:], records + [records[-1]]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                c.decode_log(("\n".join(c.canonical(r) for r in rows) + "\n").encode())

    def test_whole_log_resealing_and_suffix_removal_are_not_detectable(self):
        # Explicit counterexample to tamper-proof or truth claims, not a hardening feature.
        self.install([observation("a", "validity", "valid", 1),
                      observation("b", "payment", "paid", 2)])
        rows = [r["event"] for r in c.load(self.log)]
        rows[0]["data"]["value"] = "invalid"
        resealed = c.records_from_events(rows)
        raw = ("\n".join(c.canonical(r) for r in resealed) + "\n").encode()
        self.assertEqual(len(c.decode_log(raw)), 2)
        prefix = self.log.read_bytes().splitlines(keepends=True)[0]
        self.assertEqual(len(c.decode_log(prefix)), 1)

    def test_malformed_existing_log_prevents_append(self):
        self.log.write_bytes(b"bad\n")
        before = self.log.read_bytes()
        with self.assertRaises(ValueError):
            c.append(self.log, observation("a", "workflow", "draft", 1))
        self.assertEqual(self.log.read_bytes(), before)

    def test_cooperating_writer_lock_refuses_instead_of_blocking(self):
        self.install([observation("a", "workflow", "draft", 1)])
        with self.log.open("rb") as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assert_rejected_unchanged(observation("b", "workflow", "submitted", 2))

    def test_regular_file_and_symlink_boundaries(self):
        target = self.root / "target"
        target.write_bytes(b"")
        self.log.symlink_to(target)
        with self.assertRaises(OSError):
            c.append(self.log, observation("a", "workflow", "draft", 1))
        self.assertEqual(target.read_bytes(), b"")
        self.log.unlink()
        os.mkfifo(self.log)
        with self.assertRaises(ValueError):
            c.load(self.log)

    def test_backfilled_observation_does_not_become_current(self):
        rows = [observation("new", "validity", "valid", 2),
                observation("late_old", "validity", "invalid", 3, observed=1)]
        v = self.install(rows)
        self.assertEqual(path_get(v, ax("validity")), "valid")
        self.assertEqual(path_get(v, ax("validity", "last_observation/id")), c.digest(rows[0]))

    def test_equal_observed_time_has_explicit_append_order_tie_break(self):
        v = self.install([observation("a", "validity", "valid", 1),
                          observation("b", "validity", "invalid", 2, observed=1)])
        self.assertEqual(path_get(v, ax("validity")), "invalid")

    def test_missing_self_forward_cycles_and_cross_case_dependencies_rejected(self):
        a = observation("a", "validity", "valid", 1)
        self.install([a])
        for deps in [["self"], ["future"], ["cycle_b"], [c.digest(a), c.digest(a)]]:
            self.assert_rejected_unchanged(event("bad", "interpretation", 2, {"claim": "Unsupported"}, deps))
        foreign = event("foreign", "interpretation", 2, {"claim": "Cross-case"}, [c.digest(a)])
        foreign["case"] = "other"
        self.assert_rejected_unchanged(foreign)

    def test_invalidated_dependency_cannot_be_laundered(self):
        # Corrections target an observation with a declared compatible replacement;
        # dependents cannot be reauthored by linking back to the invalidated claim.
        rows = resolve(scenarios()[4]["events"][:6])
        self.install(rows)
        old = c.digest(rows[0])
        self.assert_rejected_unchanged(event("launder", "interpretation", 7,
                                             {"claim": "Try old evidence again"}, [old]))

    def test_correction_retraction_rejected_and_replacement_chain_never_resurrects_packet(self):
        rows = resolve(scenarios()[4]["events"])
        v = self.install(rows)
        self.assertEqual(v["cases"]["synthetic"]["handoffs"][0]["state"], "review_required")
        self.assertEqual(len(v["invalidated"]), 5)
        self.assert_rejected_unchanged(event("retract", "correction", 9, {
            "target": c.digest(rows[5]), "replacement": c.digest(rows[7]), "reason": "Retract correction"}))

    def test_correction_requires_same_axis_and_independent_replacement(self):
        rows = resolve([observation("root", "validity", "valid", 1),
                        observation("other", "workflow", "draft", 2),
                        event("dependent", "interpretation", 3, {"claim": "Depends on root"}, ["root"])])
        self.install(rows)
        self.assert_rejected_unchanged(event("wrong_axis", "correction", 4, {
            "target": c.digest(rows[0]), "replacement": c.digest(rows[1]), "reason": "Wrong axis"}))
        first = event("i1", "interpretation", 4, {"claim": "First"}, [c.digest(rows[0])])
        c.append(self.log, first)
        second = event("i2", "interpretation", 5, {"claim": "Derived from first"}, [c.digest(first)])
        c.append(self.log, second)
        self.assert_rejected_unchanged(event("circular", "correction", 6, {
            "target": c.digest(first), "replacement": c.digest(second), "reason": "Circular replacement"}))

    def test_negative_alternative_grounds_preserved(self):
        rows = resolve([
            observation("slots", "slots", "unavailable", 1),
            observation("invalid", "validity", "invalid", 2),
            event("negative", "decision", 3, {"type": "negative", "reason": "Two sufficient exclusions",
                  "grounds": [["slots"], ["invalid"]], "reopen_when": c.REOPEN}, ["slots", "invalid"]),
            observation("available", "slots", "available", 4)])
        self.install(rows)
        reopen = event("early", "decision", 5, {"type": "reopen", "negative_id": c.digest(rows[2]),
                       "reason": "Only one reason changed"}, [c.digest(rows[3])])
        self.assert_rejected_unchanged(reopen)
        valid = observation("valid", "validity", "valid", 5)
        c.append(self.log, valid)
        reopen["key"] = "review"; reopen["recorded_at"] = t(6)
        reopen["depends_on"].append(c.digest(valid))
        c.append(self.log, reopen)
        self.assertEqual(c.view(self.log, t(6))["negatives"][0]["standing"], "reopened_for_review")

    def test_same_value_stale_or_unrelated_premise_cannot_reopen_negative(self):
        base = scenarios()[5]["events"][:2]
        for observation_row, at in [
                (observation("same", "slots", "unavailable", 3), 4),
                (observation("unrelated", "validity", "valid", 3), 4),
                (observation("expired", "slots", "available", 3, until=4), 5)]:
            rows = resolve(base + [observation_row])
            with self.subTest(key=observation_row["key"]), self.assertRaises(ValueError):
                c.records_from_events(rows + [event("bad_reopen", "decision", at, {
                    "type": "reopen", "negative_id": c.digest(rows[1]), "reason": "No fresh change"},
                    [c.digest(rows[-1])])])

    def test_correction_of_negative_premise_requires_review_and_can_reopen_on_changed_value(self):
        rows = resolve(scenarios()[5]["events"][:2] + [
            observation("changed", "slots", "available", 3),
            event("fix", "correction", 4, {"target": "no_slots", "replacement": "changed", "reason": "Fix"}),
            event("reopen", "decision", 5, {"type": "reopen", "negative_id": "negative", "reason": "Review"},
                  ["changed"])])
        v = self.install(rows)
        self.assertEqual(v["negatives"][0]["standing"], "reopened_for_review")
        self.assertEqual(len(v["invalidated"]), 2)

    def test_failed_read_does_not_refresh_timestamp_or_window(self):
        rows = resolve(scenarios()[6]["events"][:2])
        self.install(rows)
        last = c.view(self.log, t(101))["cases"]["synthetic"]["axes"]["validity"]
        self.assertEqual(last["state"], "stale")
        self.assertIsNone(last["current_value"])
        self.assertEqual(last["last_observation"]["observed_at"], t(1))
        self.assertEqual(last["last_observation"]["valid_until"], t(100))

    def test_backfilled_failure_does_not_override_newer_success(self):
        v = self.install([observation("success", "validity", "valid", 2),
                          event("old_failure", "collection_failure", 3,
                                {"axis": "validity", "attempted_at": t(1), "error_code": "timeout"})])
        self.assertEqual(path_get(v, ax("validity")), "valid")

    def test_stale_answer_requires_review_instead_of_reasking(self):
        rows = resolve(scenarios()[7]["events"][:4])
        self.install(rows)
        v = c.view(self.log, t(3601))
        self.assertEqual(v["requests"][0]["state"], "answer_needs_review")
        self.assertEqual(v["unresolved_human_actions"][0]["action"], "review_answer")

    def test_same_value_correction_reviews_answer_without_reasking(self):
        rows = resolve(scenarios()[7]["events"][:4] + [
            observation("same_corrected", "slots", "unavailable", 5),
            event("fix", "correction", 6, {"target": "premise", "replacement": "same_corrected",
                  "reason": "Correct citation without changing value"})])
        v = self.install(rows)
        self.assertEqual(v["requests"][0]["state"], "answer_needs_review")
        self.assertEqual(v["unresolved_human_actions"][0]["action"], "review_answer")

    def test_changed_question_text_cannot_hide_under_answered_key(self):
        rows = resolve(scenarios()[7]["events"][:3])
        self.install(rows)
        self.assert_rejected_unchanged(event("different_question", "request", 4,
            {"question_key": "route", "question": "Approve unrelated action?"}, [c.digest(rows[0])]))

    def test_backfilled_request_cannot_reopen_answered_current_question(self):
        rows = resolve(scenarios()[7]["events"])
        self.install(rows)
        self.assert_rejected_unchanged(event("old_request", "request", 10,
            {"question_key": "route", "question": "Which route should be reviewed?"}, [c.digest(rows[0])]))

    def test_human_label_is_not_identity_or_authorization(self):
        rows = resolve(scenarios()[7]["events"][:3])
        v = self.install(rows)
        self.assertEqual(rows[-1]["actor_claim"], "human")
        self.assertIn("unauthenticated", v["trust_notice"])
        self.assertEqual(v["requests"][0]["state"], "answered_recorded")
        self.assertNotIn("authorized", v)
        imported = observation("import", "validity", "valid", 4)
        imported["role"] = "human"
        self.assert_rejected_unchanged(imported)

    def test_historical_packet_expires_even_after_new_same_value_observation(self):
        rows = resolve([observation("old", "validity", "valid", 1, until=3),
                        event("packet", "handoff", 2, {"summary": "Based on an expiring observation"}, ["old"]),
                        observation("new", "validity", "valid", 4, until=100)])
        v = self.install(rows)
        self.assertEqual(path_get(v, ax("validity")), "valid")
        self.assertEqual(v["cases"]["synthetic"]["handoffs"][0]["state"], "review_required")

    def test_projection_determinism_roundtrip_input_preservation_and_time_boundary(self):
        rows = resolve(scenarios()[4]["events"])
        original = copy.deepcopy(rows)
        first = self.install(rows)
        self.assertEqual(first, c.view(self.log, t(8)))
        self.assertEqual(rows, original)
        self.assertEqual(c.load(self.log), c.records_from_events(rows))
        with self.assertRaises(ValueError):
            c.view(self.log, t(7))

    def test_saved_view_is_bound_to_tip_and_explicit_time_and_no_overwrite(self):
        first = observation("a", "workflow", "draft", 1)
        self.install([first])
        v = c.view(self.log, t(2))
        out = self.root / "views"
        c.write_views(v, out)
        with self.assertRaises(FileExistsError):
            c.write_views(v, out)
        self.assertEqual(len(list(out.iterdir())), 4)
        c.append(self.log, observation("b", "workflow", "submitted", 2))
        self.assertNotEqual(json.loads((out / "view.json").read_text()), c.view(self.log, t(2)))

    def test_size_limits_and_empty_log(self):
        self.log.write_bytes(b"")
        self.assertEqual(c.view(self.log, t(1))["cases"], {})
        with self.assertRaises(ValueError):
            c.decode_log(b"x" * (c.MAX_BYTES + 1))

    def test_cli_append_validate_views_and_cached_view_refusal(self):
        rows = resolve(scenarios()[4]["events"])
        def cli(*args, expected=0):
            result = subprocess.run([sys.executable, str(HERE / "continuity.py"), *map(str, args)],
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            return result.stdout + result.stderr
        event_file = self.root / "event.json"
        for row in rows[:4]:
            event_file.write_text(json.dumps(row))
            cli("append", self.log, event_file)
        self.assertIn("PASS", cli("validate", self.log))
        out = self.root / "views"
        cli("views", self.log, "--at", t(8), "--out", out)
        self.assertIn("PASS", cli("check-view", self.log, out / "view.json"))
        original_snapshot = (out / "view.json").read_text()
        changed_snapshot = json.loads(original_snapshot)
        changed_snapshot["version"] = True
        (out / "view.json").write_text(json.dumps(changed_snapshot))
        self.assertIn("needs review", cli("check-view", self.log, out / "view.json", expected=2))
        (out / "view.json").write_text(original_snapshot)
        for row in rows[4:]:
            c.append(self.log, row)
        self.assertIn("needs review", cli("check-view", self.log, out / "view.json", expected=2))

    def test_runtime_has_no_network_model_or_command_execution_imports(self):
        allowed = {"__future__", "argparse", "copy", "datetime", "fcntl", "hashlib",
                   "json", "os", "pathlib", "re", "stat", "sys"}
        tree = ast.parse((HERE / "continuity.py").read_text())
        imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        imports.update(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                       for alias in node.names)
        self.assertTrue(imports <= allowed, imports)
        # This checks this revision's imports, not a sandbox against a hostile Python edit.


if __name__ == "__main__":
    unittest.main()
