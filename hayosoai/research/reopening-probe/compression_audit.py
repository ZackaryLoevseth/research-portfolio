#!/usr/bin/env python3
"""An exact finite audit of a stipulated lossy handoff, not an LLM evaluation.
Python 3.10+, standard library. No network, private data, or model calls.
Run: python compression_audit.py --out compression_audit.json
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import itertools
import json
from pathlib import Path


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def monotone_tables() -> list[tuple[int, ...]]:
    # Independent enumeration of all truth tables; no antichain generator.
    return [table for table in itertools.product((0, 1), repeat=8)
            if all(not table[a] or table[b]
                   for a in range(8) for b in range(8) if a & b == a)]


def sufficient_sets(table: tuple[int, ...]) -> list[int]:
    return [mask for mask in range(8) if table[mask] and
            not any(table[sub] and sub != mask and sub & mask == sub
                    for sub in range(8))]


def audit() -> dict:
    tables = monotone_tables()
    require(len(tables) == 20, 'Unexpected monotone rule count')
    groups: dict[tuple, list[dict]] = defaultdict(list)
    exact_checks = 0
    for number, table in enumerate(tables):
        terms = sufficient_sets(table)
        union = 0
        for term in terms:
            union |= term
        for active in range(8):
            full = int(any(active & term == term for term in terms))
            require(full == table[active], 'DNF reconstruction does not match truth table')
            exact_checks += 1
            # Deliberately discard the arrangement of reasons. A history ID is
            # NOT retained; otherwise an external lookup could restore the rule.
            key = (table[7], union, active)
            groups[key].append({'rule': number, 'excluded': table[active]})
    ambiguous = []
    minimum_errors = 0
    for (initial, union, active), rows in sorted(groups.items()):
        excluded = sum(row['excluded'] for row in rows)
        reconsider = len(rows) - excluded
        minimum_errors += min(excluded, reconsider)
        if excluded and reconsider:
            ambiguous.append({'initial_excluded': bool(initial),
                              'flat_dependencies': [p for i, p in enumerate('pqr') if union & (1 << i)],
                              'supported_after_update': [p for i, p in enumerate('pqr') if active & (1 << i)],
                              'compatible_excluded_histories': excluded,
                              'compatible_reconsider_histories': reconsider})
    require(len(groups) == 72 and len(ambiguous) == 18, 'Ambiguity totals changed')
    require(minimum_errors == 24, 'Forced-choice optimum changed')
    collision_a = [3, 4]  # (p AND q) OR r
    collision_b = [1, 6]  # p OR (q AND r)
    require(any(4 & x == x for x in collision_a), 'A should remain excluded')
    require(not any(4 & x == x for x in collision_b), 'B should reopen')
    return {
        'artifact': 'HayosoAi finite handoff-compression audit', 'version': '0.1.0',
        'status': 'PASS',
        'experiment_kind': 'Exact enumeration of a declared finite model; no LLM trials',
        'scope': {'premises': ['p', 'q', 'r'], 'rules': 'All nonredundant monotone Boolean exclusion rules',
                  'initial_state': 'All premises supported',
                  'updates': 'All eight subsets of premises retained as supported',
                  'coverage': 'Complete within the declared rule model',
                  'compressed_input': ['initial exclusion verdict', 'unordered union of dependencies', 'updated premise support'],
                  'not_available_to_decoder': ['rule structure', 'history identifier', 'original transcript', 'external rule lookup'],
                  'loss_of_support': 'Not a claim that the premise is false'},
        'rule_count': 20, 'rule_update_pairs': 160,
        'truth_table_to_support_set_checks': exact_checks,
        'distinct_compressed_inputs': len(groups), 'ambiguous_compressed_inputs': len(ambiguous),
        'rule_update_pairs_in_ambiguous_groups': sum(x['compatible_excluded_histories'] + x['compatible_reconsider_histories'] for x in ambiguous),
        'minimum_forced_choice_errors_under_uniform_rule_update_weight': minimum_errors,
        'maximum_correct_forced_choices_under_same_weight': 160 - minimum_errors,
        'ambiguities': ambiguous, 'model_calls': 0, 'human_participants': 0,
        'interpretation': 'The deliberately lossy encoding cannot support every update correctly. Faithful prose and structured records can both retain the rule. Abstention can avoid forced-choice errors; it does not recover the lost rule.',
        'limitations': ['Uniform weighting is stipulated, not an estimated real-world distribution.',
                       'No finding about any deployed memory product or AI model.',
                       'The original source may resolve the uncertainty when retrieval is available.',
                       'Removing exclusion support neither establishes the candidate nor grants permissions.',
                       'The implementation and its checks are AI-assisted, not independent human review.'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = audit()
    report['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    text = json.dumps(report, indent=2) + '\n'
    if args.out:
        args.out.write_text(text, encoding='utf-8')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
