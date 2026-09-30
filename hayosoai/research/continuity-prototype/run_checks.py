#!/usr/bin/env python3
"""One command: deterministic regression/integrity tests and fair artifact comparison."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
from compare import compare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Save inspectable artifacts to a NEW directory")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(here), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    if not result.wasSuccessful():
        return 1
    if args.out:
        report = compare(args.out)
    else:
        with tempfile.TemporaryDirectory() as temp:
            report = compare(Path(temp) / "comparison")
    print(json.dumps({k: report[k] for k in ("scenario_count", "checkpoint_count",
          "rubric_assertions_per_representation", "passing_scenarios", "source_history_fidelity",
          "final_artifact_bytes_total", "source_lines")}, indent=2))
    print("PASS. Synthetic software checks only; no human/time/model improvements measured.")
    if args.out:
        print("Artifacts: " + str(args.out.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
