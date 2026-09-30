from pathlib import Path
import tempfile
import unittest

from compare import compare, evaluate, handoff_summary, inventory, read_handoff, status_file
from fixtures import resolve, scenarios, t


class BaselineTests(unittest.TestCase):
    def test_baselines_retain_full_shared_source_history_and_uncertainty(self):
        events = resolve(scenarios()[4]["events"])
        facts = {"unknown": None, "review": "review_required"}
        status = status_file(events, t(8), facts)
        actual, history = read_handoff(handoff_summary(events, t(8), facts))
        self.assertEqual(actual, facts)
        self.assertEqual(status["source_history"], history)
        self.assertEqual(history, inventory(events))
        self.assertEqual(history[-1]["event"]["kind"], "correction")

    def test_comparison_detects_wrong_and_missing_outcomes(self):
        errors = evaluate({"draft": "submitted", "paid": None}, {"draft": "draft", "paid": "paid", "missing": None})
        self.assertEqual(len(errors), 3)

    def test_all_maintained_representations_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "comparison"
            report = compare(out)
            self.assertEqual(report["passing_scenarios"],
                             {"event_ledger": 10, "status_file": 10, "handoff_summary": 10})
            self.assertTrue(all(not any(row["errors"].values()) for row in report["details"]))
            with self.assertRaises(FileExistsError):
                compare(out)
