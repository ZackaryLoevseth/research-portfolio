#!/usr/bin/env python3
"""HayosoAi exploratory handoff pilot, protocol 0.1 (2026-09-19).

Prospective specification: 12 constructed cases x 4 memory conditions = 48
fresh-context inferences. This tests a receiver, NOT spontaneous summarization,
an agent's memory manager, real-world permissions, or general AI safety.
Conditions cross reasons retained/flattened with prose/JSON representation.
Correct UNKNOWN answers are rewarded when available information is insufficient.
No prompt tuning, model switching, retries, or selective removal after outputs.
One seed per inference; one sample only; descriptive counts, no population claim.
All stimuli, instructions and labels are committed before inference. They are
public development material, not secret held-out data or a registered study.
No full-history baseline in this first harness pilot; no token-length matching.
Code, cases, and scoring are AI-authored; no independent human review claimed.

Local: python handoff_pilot.py --self-test | --manifest | --run
--self-test and --manifest need only Python 3.10+. --run uses pinned public model
weights on CPU, with no inference service, account secrets, or external actions.
Model: https://huggingface.co/Qwen/Qwen3-0.6B (Apache-2.0, weights not distributed).
Project: https://github.com/ZackaryLoevseth/research-portfolio
No new license is granted to other portfolio assets by this file.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import time
from typing import Any

MODEL = 'Qwen/Qwen3-0.6B'
REVISION = 'c1899de289a04d12100db370d81485cdf75e47ca'
SEED = 20260919
CONDITIONS = ('prose_reasons', 'json_reasons', 'prose_flat', 'json_flat')
LABELS = ('KEEP', 'REOPEN', 'UNKNOWN')
INSTRUCTIONS = '''Decide a fictional research route's status from the supplied memory and ordered updates.
A supported premise is active. Withdrawn or refuted premises are inactive for support; withdrawal is not proof of falsity. Apply updates in order; a later update replaces an earlier state.
A sufficient ground contains premises that must ALL be active together. Grounds are alternatives: ANY one live ground suffices to keep the exclusion. JSON any_of lists alternatives; all_of lists jointly required premises. Rules use only AND and OR, no negation or unconditional ground.
KEEP: a recorded sufficient ground remains live.
REOPEN: no recorded sufficient ground remains and the record has complete coverage.
UNKNOWN: the available memory does not justify either conclusion.
Partial coverage means other, unrecorded grounds may exist: a live recorded ground still justifies KEEP, but no live recorded ground only justifies UNKNOWN.
If the AND/OR structure was lost, consider every monotone AND/OR arrangement using exactly the listed premise names, consistent with the previous exclusion. Return KEEP or REOPEN only when every possible arrangement justifies that same answer; otherwise return UNKNOWN.
Reopening is not acceptance and does not authorize any external action. You are only classifying a record.
Output exactly one word: KEEP, REOPEN, or UNKNOWN. Do not give an explanation.'''


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def cases() -> list[dict[str, Any]]:
    a = [['p', 'q'], ['r']]
    b = [['p'], ['q', 'r']]
    specs = [
        (a, [{'p': 'withdrawn', 'q': 'withdrawn'}], 'complete'),
        (b, [{'p': 'withdrawn', 'q': 'withdrawn'}], 'complete'),
        ([['p', 'q']], [{'p': 'withdrawn'}], 'complete'),
        ([['p'], ['q']], [{'p': 'withdrawn'}], 'complete'),
        (a, [], 'complete'),
        (b, [{'p': 'withdrawn', 'q': 'withdrawn', 'r': 'withdrawn'}], 'complete'),
        (a, [{'p': 'withdrawn'}, {'r': 'withdrawn'}], 'complete'),
        ([['p'], ['q']], [{'p': 'withdrawn'}, {'q': 'withdrawn'}], 'complete'),
        ([['p'], ['q']], [{'p': 'withdrawn'}, {'q': 'withdrawn'}, {'q': 'supported'}], 'complete'),
        (a, [{'p': 'withdrawn', 'q': 'withdrawn'}], 'partial'),
        (a, [{'p': 'withdrawn'}, {'r': 'withdrawn'}], 'partial'),
        ([['p']], [{'p': 'refuted'}], 'partial'),
    ]
    return [{'id': f'C{i:02d}', 'grounds': grounds, 'updates': updates,
             'coverage': coverage} for i, (grounds, updates, coverage) in enumerate(specs, 1)]


def names(case: dict) -> list[str]:
    return sorted({p for ground in case['grounds'] for p in ground})


def final_states(case: dict) -> dict[str, str]:
    states = {p: 'supported' for p in names(case)}
    for update in case['updates']:
        if any(p not in states or s not in ('supported', 'withdrawn', 'refuted')
               for p, s in update.items()):
            raise ValueError('Malformed constructed update')
        states.update(update)
    return states


def decide(grounds: list[list[str]], states: dict[str, str], coverage: str) -> str:
    if any(all(states[p] == 'supported' for p in ground) for ground in grounds):
        return 'KEEP'
    return 'REOPEN' if coverage == 'complete' else 'UNKNOWN'


def possible_rules(premises: list[str]) -> list[list[list[str]]]:
    # All nonredundant monotone rules using exactly these names, no empty ground.
    subsets = [frozenset(s) for n in range(1, len(premises) + 1)
               for s in itertools.combinations(premises, n)]
    out = []
    for mask in range(1, 1 << len(subsets)):
        family = [s for i, s in enumerate(subsets) if mask & (1 << i)]
        if set().union(*family) != set(premises):
            continue
        if any(x < y or y < x for x, y in itertools.combinations(family, 2)):
            continue
        out.append([sorted(s) for s in family])
    return out


def expected(case: dict, condition: str) -> str:
    states = final_states(case)
    rules = possible_rules(names(case)) if condition.endswith('_flat') else [case['grounds']]
    labels = {decide(rule, states, case['coverage']) for rule in rules}
    if not labels:
        raise ValueError('No compatible underlying record')
    return next(iter(labels)) if len(labels) == 1 else 'UNKNOWN'


def prompt(case: dict, condition: str) -> str:
    ids = names(case)
    retained = condition.endswith('_reasons')
    memory = {'initial_state': {p: 'supported' for p in ids},
              'previous_disposition': 'excluded', 'coverage': case['coverage']}
    if retained:
        memory['reasons'] = {'any_of': [{'all_of': g} for g in case['grounds']]}
    else:
        memory['reasons'] = {'premise_names': ids, 'and_or_structure': 'lost'}
    if condition.startswith('json_'):
        return json.dumps({'memory': memory, 'ordered_updates': case['updates']}, sort_keys=True)
    lines = ['All of these premises were initially supported: ' + ', '.join(ids) + '.',
             'The previous disposition was excluded.',
             'The recorded grounds have ' + case['coverage'] + ' coverage.']
    if retained:
        grounds = ['(' + ' AND '.join(g) + ')' for g in case['grounds']]
        lines.append('The sufficient recorded grounds are alternatives: ' + ' OR '.join(grounds) + '.')
    else:
        lines.append('Only the premise names were retained: ' + ', '.join(ids) +
                     '. The AND/OR structure of the reasons was lost.')
    if not case['updates']:
        lines.append('There are no updates.')
    for i, update in enumerate(case['updates'], 1):
        lines.append(f'Update {i}: ' + '; '.join(p + ' becomes ' + s for p, s in sorted(update.items())) + '.')
    return '\n'.join(lines)


def manifest() -> dict[str, Any]:
    rows = []
    for case in cases():
        for condition in CONDITIONS:
            text = prompt(case, condition)
            rows.append({'case_id': case['id'], 'condition': condition,
                         'user_prompt': text, 'prompt_sha256': digest(text.encode()),
                         'expected': expected(case, condition)})
    return {'protocol': 'HayosoAi receiver pilot 0.1', 'model': MODEL,
            'model_revision': REVISION, 'generation_seed_each_call': SEED,
            'decoding': {'enable_thinking': False, 'do_sample': True,
                         'temperature': 0.7, 'top_p': 0.8, 'top_k': 20,
                         'max_new_tokens': 16},
            'system_prompt': INSTRUCTIONS, 'cases': cases(), 'rows': rows}


def self_test() -> dict:
    if not __debug__:
        raise ValueError('Self-tests require assertions enabled')
    data = manifest()
    assert len(data['rows']) == 48
    assert len({(r['case_id'], r['condition']) for r in data['rows']}) == 48
    full_labels = ['KEEP', 'REOPEN', 'REOPEN', 'KEEP', 'KEEP', 'REOPEN',
                   'REOPEN', 'REOPEN', 'KEEP', 'KEEP', 'UNKNOWN', 'UNKNOWN']
    flat_labels = ['UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'KEEP', 'REOPEN',
                   'UNKNOWN', 'REOPEN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', 'UNKNOWN']
    for i, case in enumerate(cases()):
        assert expected(case, 'prose_reasons') == full_labels[i]
        assert expected(case, 'json_reasons') == full_labels[i]
        assert expected(case, 'prose_flat') == flat_labels[i]
        assert expected(case, 'json_flat') == flat_labels[i]
        # Representation changes no data; parsed JSON reproduces the generated memory.
        parsed = json.loads(prompt(case, 'json_reasons'))
        assert parsed['ordered_updates'] == case['updates']
        assert [x['all_of'] for x in parsed['memory']['reasons']['any_of']] == case['grounds']
    # Indistinguishable memories must be scored alike, not against hidden answers.
    for condition in ('prose_flat', 'json_flat'):
        assert prompt(cases()[0], condition) == prompt(cases()[1], condition)
        assert expected(cases()[0], condition) == expected(cases()[1], condition) == 'UNKNOWN'
        assert prompt(cases()[2], condition) == prompt(cases()[3], condition)
    assert [len(possible_rules(list('pqr')[:n])) for n in (1, 2, 3)] == [1, 2, 9]
    return {'status': 'PASS', 'cases': 12, 'planned_inferences': 48,
            'manifest_sha256': digest(encoded(data)), 'model_inferences_executed': 0,
            'label_counts_by_information': {
                'reasons': dict(collections.Counter(full_labels)),
                'flat': dict(collections.Counter(flat_labels))},
            'limitations': 'Software preflight only; no model result.'}


def run() -> int:
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    check = self_test()
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    data = manifest()
    source_sha = digest(Path(__file__).read_bytes())
    metadata = {'source_sha256': source_sha, 'manifest_sha256': check['manifest_sha256'],
                'git_commit': os.environ.get('GITHUB_SHA'), 'model': MODEL, 'revision': REVISION,
                'torch': torch.__version__, 'transformers': transformers.__version__,
                'python': platform.python_version(), 'cpu_threads': torch.get_num_threads(),
                'platform': platform.platform(), 'device': 'cpu', 'dtype': 'float32',
                'decoding': data['decoding'], 'seed_each_call': SEED,
                'energy_water_emissions': 'unmeasured', 'paid_inference_calls': 0}
    print('PILOT_METADATA ' + json.dumps(metadata), flush=True)
    load_start = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION,
                trust_remote_code=False, use_safetensors=True,
                torch_dtype=torch.float32, attn_implementation='sdpa')
    model.eval()
    metadata['load_seconds'] = round(time.perf_counter() - load_start, 4)
    metadata['actual_parameter_count'] = sum(p.numel() for p in model.parameters())
    order = list(data['rows'])
    random.Random(SEED).shuffle(order)
    results = []
    start = time.perf_counter()
    for spec in order:
        if time.perf_counter() - start > 600:
            print('PILOT_STOP inference wall-time cap reached', flush=True)
            break
        messages = [{'role': 'system', 'content': INSTRUCTIONS},
                    {'role': 'user', 'content': spec['user_prompt']}]
        rendered = tok.apply_chat_template(messages, tokenize=False,
                    add_generation_prompt=True, enable_thinking=False)
        inputs = tok(rendered, return_tensors='pt')
        torch.manual_seed(SEED)
        before = time.perf_counter()
        with torch.inference_mode():
            output = model.generate(**inputs, do_sample=True, temperature=0.7,
                     top_p=0.8, top_k=20, max_new_tokens=16,
                     pad_token_id=tok.eos_token_id)
        generated = output[0, inputs['input_ids'].shape[1]:].tolist()
        raw = tok.decode(generated, skip_special_tokens=True)
        answer = raw.strip()
        row = {k: spec[k] for k in ('case_id', 'condition', 'prompt_sha256', 'expected')}
        row.update(raw_output=raw, predicted=answer if answer in LABELS else 'INVALID',
                   valid=answer in LABELS, correct=answer == spec['expected'],
                   input_tokens=inputs['input_ids'].shape[1], output_tokens=len(generated),
                   generated_token_ids=generated, rendered_prompt_sha256=digest(rendered.encode()),
                   wall_seconds=round(time.perf_counter() - before, 4),
                   hit_token_cap=len(generated) >= 16)
        results.append(row)
        print('PILOT_ROW ' + json.dumps(row), flush=True)
    groups = {}
    for condition in CONDITIONS:
        rr = [r for r in results if r['condition'] == condition]
        groups[condition] = {'completed': len(rr), 'planned': 12,
            'correct': sum(r['correct'] for r in rr), 'valid': sum(r['valid'] for r in rr),
            'unsupported_determinate': sum(r['expected'] == 'UNKNOWN' and r['predicted'] in ('KEEP','REOPEN') for r in rr),
            'unnecessary_unknown': sum(r['expected'] != 'UNKNOWN' and r['predicted'] == 'UNKNOWN' for r in rr),
            'input_tokens': sum(r['input_tokens'] for r in rr),
            'output_tokens': sum(r['output_tokens'] for r in rr),
            'wall_seconds': round(sum(r['wall_seconds'] for r in rr), 4)}
    report = {'status': 'COMPLETE' if len(results) == 48 else 'INCOMPLETE',
              'metadata': metadata, 'groups': groups, 'rows': results,
              'inference_seconds': round(time.perf_counter() - start, 4),
              'limitations': 'One small model; one sample per constructed prompt; not token-matched; not an agent/memory-creation evaluation; not independent human review; no efficacy, novelty, or general safety claim.'}
    Path('pilot_results.json').write_text(json.dumps(report, indent=2) + '\n')
    Path('pilot_manifest.json').write_text(json.dumps(data, indent=2) + '\n')
    print('PILOT_SUMMARY ' + json.dumps({k:v for k,v in report.items() if k != 'rows'}), flush=True)
    return 0 if len(results) == 48 else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--manifest', action='store_true')
    group.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
    elif args.manifest:
        print(json.dumps(manifest(), indent=2))
    else:
        return run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
