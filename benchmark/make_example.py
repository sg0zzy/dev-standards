#!/usr/bin/env python3
"""Write explicitly synthetic example reports, without HTTP or hardware access."""
import argparse
from pathlib import Path
import suite as b


def generate(root):
    root.mkdir(parents=True, exist_ok=False)
    paths = []
    for profile, decode, prefill in [('baseline-96', 48.0, 1000.0), ('uma-64', 47.5, 1020.0), ('uma-512m', 46.0, 980.0)]:
        path = root / profile
        path.mkdir()
        records = []
        for i in range(5):
            records.append({'id': f'throughput-4096-{i}', 'kind': 'throughput', 'target': 4096,
                'status': 'ok', 'input_tokens': 4096, 'generated_tokens': 512, 'fresh_input_tokens': 4080, 'cached_tokens': 16,
                'effective_expert_slots': 24576, 'prefill_tps': prefill + i - 2,
                'decode_tps': decode + (i-2)*.1, 'ttft_s': 4.2 + i*.01, 'wall_s': 15.0 + i*.1,
                'warnings': ['SIMULATED EXAMPLE; NOT MEASURED']})
        records.append({'id': 'recall-131072', 'kind': 'recall', 'status': 'ok', 'exact_match': False,
                        'warnings': ['SIMULATED FAILURE; NOT A MODEL EVALUATION']})
        session = {'schema': b.SCHEMA, 'protocol': b.PROTOCOL, 'profile': profile, 'status': 'complete',
            'synthetic_example': True, 'identity': {'synthetic_example': True, 'workload': 'example-only'},
            'planned_cases': [{k: v for k, v in r.items() if k in ('id', 'kind', 'target')} for r in records],
            'warnings': ['SIMULATED EXAMPLE ONLY. All rates, timings, settings and outcomes are invented to demonstrate formatting.',
                         'No system, memory, I/O or model metadata was measured. Fields are omitted rather than fabricated.'],
            'kernel_events': {'coverage': 'unavailable', 'events': []}}
        b.write(path / 'session.json', session)
        for r in records:
            b.append(path / 'runs.jsonl', r)
        b.report(path, session, records)
        paths.append(path)
    b.compare(paths, root / 'comparison')
    (root / 'README.md').write_text('# Synthetic example output\n\n'
        '**All numbers and outcomes here are invented formatting examples.** No inference was run.\n\n'
        'These abbreviated sessions demonstrate five repetitions, variability, percentage changes and a recall failure; '
        'they are not a full 38-request workload. Real metadata/resource data is intentionally absent.\n\n'
        'See [comparison](comparison/comparison.md) and [CSV](comparison/comparison.csv), '
        'or [one report](baseline-96/report.md). Synthetic fingerprints cannot match real runs.\n\n'
        'Regenerate into a NEW directory with `python3 benchmark/make_example.py /tmp/uma-example`.\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('output', type=Path)
    generate(p.parse_args().output)
