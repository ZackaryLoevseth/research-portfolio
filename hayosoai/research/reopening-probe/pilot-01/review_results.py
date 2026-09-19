#!/usr/bin/env python3
"""Decode and recheck the frozen pilot result without model calls or downloads.
Run in this folder: python review_results.py
AI-authored post-run analysis. This is not independent human verification.
"""
from __future__ import annotations
import base64
import collections
import hashlib
import json
from pathlib import Path
import zlib
import handoff_pilot as pilot

RAW_SHA = '1a93c668f51fc93f85bc9feab8978e8e1365b8546410dcc41ae54cb3ed3473a1'
SOURCE_SHA = 'ded05a8eff2c5bd4afa93cfb2290cd1600afc97dfdb0ea4e20481bad2c287e16'
MANIFEST_SHA = '58aaeb440ee96706a069951c95edeec06cc6829ff0bb5709ed6baea1ec06624f'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def review(root: Path) -> dict:
    require(hashlib.sha256((root / 'handoff_pilot.py').read_bytes()).hexdigest() == SOURCE_SHA,
            'Frozen source mismatch; do not score a different protocol as this run')
    text = (root / 'raw_report.b64').read_text(encoding='ascii').strip()
    require(len(text) < 100_000, 'Unexpectedly large encoded report')
    decoder = zlib.decompressobj()
    raw = decoder.decompress(base64.b64decode(text, validate=True), 100_001)
    require(decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data,
            'Incomplete, trailing, or oversized compressed report')
    require(len(raw) <= 100_000 and hashlib.sha256(raw).hexdigest() == RAW_SHA,
            'Raw report hash mismatch')
    report = json.loads(raw)
    manifest = pilot.manifest()
    require(pilot.digest(pilot.encoded(manifest)) == MANIFEST_SHA, 'Manifest mismatch')
    require(report['metadata']['source_sha256'] == SOURCE_SHA, 'Reported source mismatch')
    require(report['metadata']['manifest_sha256'] == MANIFEST_SHA, 'Reported manifest mismatch')
    expected = {(r['case_id'], r['condition']): r for r in manifest['rows']}
    seen = set()
    for row in report['rows']:
        key = (row['case_id'], row['condition'])
        require(key in expected and key not in seen, 'Unknown or duplicate case-condition')
        seen.add(key)
        spec = expected[key]
        require(row['prompt_sha256'] == spec['prompt_sha256'], 'Prompt hash mismatch')
        require(row['expected'] == spec['expected'], 'Expected answer mismatch')
        answer = row['raw_output'].strip()
        require(row['valid'] == (answer in pilot.LABELS), 'Incorrect validity flag')
        require(row['correct'] == (answer == spec['expected']), 'Incorrect scoring flag')
        require(row['predicted'] == (answer if answer in pilot.LABELS else 'INVALID'),
                'Predicted label inconsistent with raw output')
    require(seen == set(expected) and report['status'] == 'COMPLETE', 'Incomplete run')
    groups = {}
    for condition in pilot.CONDITIONS:
        rows = [r for r in report['rows'] if r['condition'] == condition]
        labels = collections.Counter(expected[(r['case_id'], condition)]['expected'] for r in rows)
        correct = sum(r['raw_output'].strip() == r['expected'] for r in rows)
        require(correct == report['groups'][condition]['correct'], 'Group total mismatch')
        groups[condition] = {'correct': correct, 'total': len(rows),
            'constant_label_baselines': dict(labels),
            'observed_answers': dict(collections.Counter(r['raw_output'].strip() for r in rows)),
            'input_tokens': sum(r['input_tokens'] for r in rows),
            'output_tokens': sum(r['output_tokens'] for r in rows)}
    output = root / 'pilot_results.json'
    if output.exists():
        require(output.read_bytes() == raw, 'Refusing to overwrite a different results file')
    else:
        output.write_bytes(raw)
    return {'complete': True, 'checked_rows': len(seen),
        'unique_prompt_texts': len({r['prompt_sha256'] for r in manifest['rows']}),
        'raw_report_sha256': RAW_SHA, 'groups': groups,
        'model_calls_this_review': 0,
        'scope': 'Integrity and descriptive rescoring by AI-authored code, not independent review or population inference.'}


if __name__ == '__main__':
    print(json.dumps(review(Path(__file__).resolve().parent), indent=2))
