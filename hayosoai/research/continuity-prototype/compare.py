"""Compare maintained baseline artifacts, NOT human/time/model performance."""
import json
from pathlib import Path

import continuity as c
from baseline_facts import FACTS
from fixtures import path_get, resolve, scenarios


def inventory(events):
    return [{"event_id": c.digest(e), "event": e} for e in events]


def status_file(events, at, facts):
    return {"as_of": at, "trust_notice": c.NOTICE, "facts": facts, "source_history": inventory(events)}


def handoff_summary(events, at, facts):
    return ("# Maintained handoff\n\nSynthetic sources only; " + c.NOTICE + "\n\nAs of " + at
            + "\n\nThe following assertions are maintained separately by the baseline author.\n"
            + "Null values retain uncertainty. Counts refer to recorded claims.\n\n"
            + "Facts:\n" + json.dumps(facts, indent=2, sort_keys=True) + "\n\n"
            + "Source history (all input fields, identifiers, timestamps and corrections retained):\n"
            + "\n".join(c.canonical(row) for row in inventory(events)) + "\n")


def read_handoff(text):
    fact_text, history = text.split("Facts:\n", 1)[1].split("\n\nSource history ", 1)
    history = history.split(":\n", 1)[1]
    return json.loads(fact_text), [c.strict_json(line) for line in history.splitlines()]


def evaluate(actual, expected):
    return [{"path": path, "expected": value, "actual": actual.get(path)}
            for path, value in expected.items() if path not in actual or actual[path] != value]


def compare(output):
    output = Path(output)
    output.mkdir()
    details = []
    totals = {"event_ledger": 0, "status_file": 0, "handoff_summary": 0}
    byte_counts = {name: 0 for name in totals}
    assertions = 0
    for scenario in scenarios():
        events = resolve(scenario["events"])
        directory = output / scenario["name"]
        directory.mkdir()
        passed = {name: True for name in totals}
        for n, check in enumerate(scenario["checks"]):
            end = next(i for i, e in enumerate(events) if e["key"] == check["after"]) + 1
            prefix = events[:end]
            records = c.records_from_events(prefix)
            projected = c.project(prefix, check["at"], records[-1]["record_hash"])
            prototype_facts = {path: path_get(projected, path) for path in check["facts"]}
            manual = FACTS[scenario["name"]][check["after"]]
            c.require(set(manual) == set(check["facts"]), "Baseline rubric fields differ")
            status = status_file(prefix, check["at"], manual)
            text = handoff_summary(prefix, check["at"], manual)
            handoff_facts, handoff_history = read_handoff(text)
            c.require(status["source_history"] == handoff_history == inventory(prefix),
                      "Baselines did not receive exactly the same source history")
            errors = {"event_ledger": evaluate(prototype_facts, check["facts"]),
                      "status_file": evaluate(json.loads(json.dumps(status))["facts"], check["facts"]),
                      "handoff_summary": evaluate(handoff_facts, check["facts"])}
            for name in totals:
                passed[name] &= not errors[name]
            assertions += len(check["facts"])
            details.append({"scenario": scenario["name"], "checkpoint": check["after"],
                            "assertions": len(check["facts"]), "errors": errors})
            if n == len(scenario["checks"]) - 1:
                checkpoint_dir = directory / "final"
                checkpoint_dir.mkdir()
                (checkpoint_dir / "status-file.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
                (checkpoint_dir / "handoff-summary.md").write_text(text)
                (checkpoint_dir / "events.jsonl").write_text("\n".join(c.canonical(r) for r in records) + "\n")
                c.write_views(projected, checkpoint_dir / "views")
                byte_counts["event_ledger"] += (checkpoint_dir / "events.jsonl").stat().st_size
                byte_counts["status_file"] += (checkpoint_dir / "status-file.json").stat().st_size
                byte_counts["handoff_summary"] += (checkpoint_dir / "handoff-summary.md").stat().st_size
        for name in totals:
            totals[name] += int(passed[name])
    here = Path(__file__).resolve().parent
    report = {
        "scenario_count": len(scenarios()), "checkpoint_count": len(details),
        "rubric_assertions_per_representation": assertions, "passing_scenarios": totals,
        "source_history_fidelity": "PASS: same events, IDs, timestamps, dependencies and corrections",
        "final_artifact_bytes_total": byte_counts,
        "source_lines": {name: len((here / name).read_text().splitlines())
                         for name in ("continuity.py", "fixtures.py", "baseline_facts.py", "compare.py",
                                      "test_continuity.py", "test_compare.py", "run_checks.py")},
        "method": "Separate literal baseline facts; complete shared input history; same checkpoint rubric. "
                  "Maintained final artifacts, not competing automated update engines or a blinded study.",
        "conclusion": "All three representations can preserve these distinctions when maintained. "
                      "The ledger adds executable validation, replay and declared-dependency review rules. "
                      "The simpler formats require fewer implementation mechanisms.",
        "limits": ["No measured human time, maintenance error rate, model performance or overall value.",
                   "Baseline assertions were authored with knowledge of these synthetic scenarios.",
                   "Byte counts compare final log vs final baseline document per scenario; ledger views "
                   "and all systems' earlier checkpoints are excluded. Formats have different verbosity.",
                   "Declared dependencies cannot discover omitted grounds or establish source truth."],
        "details": details,
    }
    (output / "comparison.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
