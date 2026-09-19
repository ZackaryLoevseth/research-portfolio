#!/usr/bin/env python3
"""HayosoAi Reopening Probe 0.1: a finite reference model, NOT a model benchmark result.

Python 3.10+, standard library only. No network, telemetry, credentials, or model calls.
Grounds are ORs of AND-sets of premise IDs. Withdrawal removes support; it does
not assert that the premise is false. Reconsideration never establishes a candidate
or grants execution permission. All cases are constructed, not observed transcripts.
Generated with ChatGPT under Zackary Loevseth's project direction, 2026-09-19.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

STATES = ('supported', 'withdrawn', 'refuted')
VERSION = '0.1.0'

def validate(record: dict[str, Any]) -> None:
    required = {'id', 'candidate', 'premises', 'grounds', 'coverage'}
    if not isinstance(record, dict) or not required.issubset(record):
        raise ValueError('Record must include id, candidate, premises, grounds, coverage')
    if not isinstance(record['id'], str) or not record['id']:
        raise ValueError('id must be a nonempty string')
    if not isinstance(record['candidate'], str) or not record['candidate']:
        raise ValueError('candidate must be a nonempty string')
    premises = record['premises']
    if not isinstance(premises, dict) or any(not isinstance(k, str) or not k for k in premises):
        raise ValueError('premises must map nonempty IDs to explicit states')
    if any(v not in STATES for v in premises.values()):
        raise ValueError('Unsupported premise state')
    if record['coverage'] not in ('complete_within_declared_scope', 'partial'):
        raise ValueError('Explicit record coverage required')
    if not isinstance(record['grounds'], list):
        raise ValueError('grounds must be a list of sufficient support sets')
    for ground in record['grounds']:
        if not isinstance(ground, list) or any(not isinstance(p, str) for p in ground):
            raise ValueError('Each ground must be a list of premise IDs')
        if len(ground) != len(set(ground)) or any(p not in premises for p in ground):
            raise ValueError('Duplicate or undeclared premise in ground')

def canonical(record: dict[str, Any]) -> str:
    validate(record)
    return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

def assess(record: dict[str, Any]) -> dict[str, Any]:
    validate(record)
    live = [list(g) for g in record['grounds']
            if all(record['premises'][p] == 'supported' for p in g)]
    status = ('excluded_under_recorded_grounds' if live else
              'reconsider' if record['coverage'] == 'complete_within_declared_scope'
              else 'insufficient_record')
    return {'id': record['id'], 'disposition': status, 'remaining_support_sets': live,
            'candidate_acceptance': 'not_derived', 'execution_permission': 'not_granted'}

def revise(record: dict[str, Any], changes: dict[str, str]) -> dict[str, Any]:
    """Return a new record; preserve reasons and original record, not just its verdict."""
    validate(record)
    if not isinstance(changes, dict) or any(k not in record['premises'] for k in changes):
        raise ValueError('Updates must refer to existing premise IDs')
    if any(v not in STATES for v in changes.values()):
        raise ValueError('Unsupported update state')
    result = json.loads(canonical(record))
    result['premises'].update(changes)
    return result

def record_for(grounds: list[list[str]], states: tuple[str, ...], identifier='case') -> dict:
    return {'id': identifier, 'candidate': 'Investigate route A; do not execute external actions.',
            'premises': dict(zip(('p', 'q', 'r'), states)), 'grounds': grounds,
            'coverage': 'complete_within_declared_scope'}

def antichains() -> list[list[list[str]]]:
    # Canonical nonredundant monotone DNF rules over three premise-support bits.
    universe = [frozenset(s) for size in range(4)
                for s in itertools.combinations(('p', 'q', 'r'), size)]
    out = []
    for mask in range(1 << len(universe)):
        family = [universe[i] for i in range(len(universe)) if mask & (1 << i)]
        if any(a < b or b < a for a, b in itertools.combinations(family, 2)):
            continue
        out.append([sorted(s) for s in family])
    return out

def bit_oracle(grounds: list[list[str]], states: tuple[str, ...]) -> bool:
    # Separate bit-mask implementation checks the list-based production evaluator.
    bits = sum(1 << i for i, state in enumerate(states) if state == 'supported')
    masks = [sum(1 << ('p', 'q', 'r').index(p) for p in g) for g in grounds]
    return any(bits & mask == mask for mask in masks)

def fixtures() -> list[dict[str, Any]]:
    rows = []
    variants = [([['p', 'q'], ['r']], ('withdrawn', 'supported', 'supported')),
                ([['p'], ['q', 'r']], ('withdrawn', 'withdrawn', 'supported')),
                ([['p', 'q'], ['r']], ('withdrawn', 'supported', 'withdrawn')),
                ([['p'], ['r']], ('refuted', 'supported', 'supported')),
                ([['p', 'q']], ('supported', 'withdrawn', 'supported')),
                ([['p', 'q']], ('supported', 'supported', 'withdrawn'))]
    for n, (g, states) in enumerate(variants, 1):
        for coverage in ('complete_within_declared_scope', 'partial'):
            item = record_for(g, states, f'dev-{n:02d}-{coverage[:1]}')
            item['coverage'] = coverage
            rows.append(item)
    return rows

def self_test() -> dict[str, Any]:
    if not __debug__:
        raise ValueError("Run self-tests without Python -O; assertions must be enabled")
    rules = antichains()
    assert len(rules) == 20
    state_checks = transitions = roundtrips = 0
    for grounds in rules:
        for states in itertools.product(STATES, repeat=3):
            record = record_for(grounds, states)
            original = canonical(record)
            result = assess(record)
            expected = bit_oracle(grounds, states)
            assert (result['disposition'] == 'excluded_under_recorded_grounds') == expected
            assert result['candidate_acceptance'] == 'not_derived'
            assert result['execution_permission'] == 'not_granted'
            state_checks += 1
            assert assess(json.loads(original)) == result
            roundtrips += 1
            for p in ('p', 'q', 'r'):
                for state in STATES:
                    changed = revise(record, {p: state})
                    new_states = tuple(changed['premises'][x] for x in ('p', 'q', 'r'))
                    actual = assess(changed)['disposition'] == 'excluded_under_recorded_grounds'
                    assert actual == bit_oracle(grounds, new_states)
                    assert changed['grounds'] == record['grounds']
                    assert canonical(record) == original
                    transitions += 1
    # A surviving alternate reason must remain available for a later update.
    r = record_for([['p'], ['q']], ('supported', 'supported', 'supported'))
    r1 = revise(r, {'p': 'withdrawn'})
    assert assess(r1)['disposition'] == 'excluded_under_recorded_grounds'
    r2 = revise(json.loads(canonical(r1)), {'q': 'withdrawn'})
    assert assess(r2)['disposition'] == 'reconsider'
    assert r2['premises']['p'] == 'withdrawn'  # not rewritten as "refuted"
    assert assess(revise(r2, {'q': 'supported'}))['disposition'] == 'excluded_under_recorded_grounds'
    partial = json.loads(canonical(r2)); partial['coverage'] = 'partial'
    assert assess(partial)['disposition'] == 'insufficient_record'
    # Same flattened dependency list, different correct update behavior.
    a = record_for([['p', 'q'], ['r']], ('withdrawn', 'withdrawn', 'supported'))
    b = record_for([['p'], ['q', 'r']], ('withdrawn', 'withdrawn', 'supported'))
    assert {x for g in a['grounds'] for x in g} == {x for g in b['grounds'] for x in g}
    assert assess(a)['disposition'] != assess(b)['disposition']
    invalid = [dict(r, coverage='unknown'), dict(r, grounds=[['missing']]),
               dict(r, grounds=[['p','p']]), dict(r, premises={'p':'false'}),
               dict(r, grounds='p'), dict(r, candidate='')]
    for bad in invalid:
        try: validate(bad)
        except ValueError: pass
        else: raise AssertionError('Invalid fixture was accepted')
    # Mutation probes are intentionally bad implementations, NOT measured AI models.
    mutations = {}
    mutations['flatten_OR_to_AND'] = (all(a['premises'][p] == 'supported' for p in ('p','q','r'))
                                      != bit_oracle(a['grounds'], tuple(a['premises'].values())))
    mutations['flatten_AND_to_OR'] = (any(b['premises'][p] == 'supported' for p in ('p','q','r'))
                                      != bit_oracle(b['grounds'], tuple(b['premises'].values())))
    mutations['reopen_after_any_withdrawal'] = assess(r1)['disposition'] != 'reconsider'
    mutations['accept_after_reopening'] = assess(r2)['candidate_acceptance'] != 'accepted'
    mutations['grant_permission_after_reopening'] = assess(r2)['execution_permission'] != 'granted'
    assert all(mutations.values())
    return {'artifact': 'HayosoAi Reopening Probe', 'version': VERSION,
            'status': 'PASS', 'nonredundant_rules': len(rules),
            'exhaustive_state_checks': state_checks, 'single_update_checks': transitions,
            'json_roundtrip_checks': roundtrips, 'invalid_inputs_rejected': len(invalid),
            'targeted_sequence_and_coverage_checks': 'PASS', 'mutation_probes_rejected': mutations,
            'model_calls': 0, 'external_actions': 0,
            'limitation': 'Finite synthetic implementation checks only. No measured LLM or human performance; no novelty or general safety claim.'}

def score(path: Path) -> dict[str, Any]:
    expected = {r['id']: assess(r) for r in fixtures()}
    seen: set[str] = set()
    correct = invalid = 0
    details = []
    for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip(): continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict): raise ValueError('Expected object')
            ident = row.get('id')
            if not isinstance(ident,str) or ident not in expected or ident in seen:
                raise ValueError('Unknown or duplicate id')
            seen.add(ident)
            keys = ('disposition', 'candidate_acceptance', 'execution_permission')
            ok = all(row.get(k) == expected[ident][k] for k in keys)
            correct += int(ok)
            details.append({'id': ident, 'correct_required_fields': ok})
        except (ValueError, TypeError) as exc:
            invalid += 1; details.append({'line': lineno, 'error': str(exc)})
    return {'total_cases': len(expected), 'correct_required_fields': correct,
            'missing': sorted(set(expected)-seen), 'invalid_rows': invalid, 'details': details,
            'limitation': 'Scores explicit fields on the public development fixtures; not a general evaluation.'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--cases', action='store_true', help='Emit public development inputs, JSONL')
    group.add_argument('--answers', action='store_true', help='Emit deterministic oracle answers, JSONL')
    group.add_argument('--score', type=Path, metavar='PREDICTIONS_JSONL')
    args = parser.parse_args()
    try:
        if args.self_test:
            report = self_test()
            report['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            print(json.dumps(report, indent=2))
        elif args.cases or args.answers:
            for row in fixtures(): print(json.dumps(assess(row) if args.answers else row, ensure_ascii=False))
        else: print(json.dumps(score(args.score), indent=2))
        return 0
    except (ValueError, OSError, AssertionError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr); return 1

if __name__ == '__main__': raise SystemExit(main())
