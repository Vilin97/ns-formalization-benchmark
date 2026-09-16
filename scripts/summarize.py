#!/usr/bin/env python3
"""Produce a comparison only from successful, complete, clean benchmark runs."""
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--oai', default='oai-run1')
p.add_argument('--leanpool', default='leanpool-preflight')
a = p.parse_args()
runs = {v: json.loads((ROOT/'results'/label/'summary.json').read_text()) for v,label in [('oai',a.oai),('leanpool',a.leanpool)]}
for v,d in runs.items():
    assert d['variant']==v and d['success'] and d['clean'] and d['completed_modules']==d['modules'], f'{v}: incomplete, failed or resumed run'
for key in ['lean','jobs','lean_threads','rss_sample_interval_seconds']:
    assert runs['oai'][key]==runs['leanpool'][key], f'Mismatched {key}'
for v in runs:
    manifest=json.loads((ROOT/v/'lake-manifest.json').read_text())
    runs[v]['dependency_revisions']={x['name']:x['rev'] for x in manifest['packages']}
assert runs['oai']['dependency_revisions']==runs['leanpool']['dependency_revisions']
o,l=runs['oai'],runs['leanpool']
comparison={'runs':runs,'oai_wall_divided_by_leanpool':o['wall_seconds']/l['wall_seconds'],
    'leanpool_wall_reduction_percent':100*(1-l['wall_seconds']/o['wall_seconds']),
    'leanpool_aggregate_rss_reduction_percent':100*(1-l['peak_aggregate_compiler_rss_bytes']/o['peak_aggregate_compiler_rss_bytes']),
    'leanpool_single_process_rss_reduction_percent':100*(1-l['peak_single_compiler_rss_bytes']/o['peak_single_compiler_rss_bytes'])}
(ROOT/'results/comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
lines=['# Local compilation results','',
    'Both builds completed successfully with the exact same Lean 4.34.0-rc2 compiler',
    'and Mathlib dependencies on this Apple M4 Pro laptop (12 cores, 48 GiB RAM, macOS 15.7.4).',
    'Four concurrent compiler processes, one Lean worker thread per process.', '',
    '| Version | Modules | Wall time | Peak aggregate compiler RSS | Peak single compiler RSS |',
    '|---|---:|---:|---:|---:|']
for v in ['oai','leanpool']:
    d=runs[v];s=d['wall_seconds']
    lines.append(f'| {"OAI original" if v=="oai" else "LeanPool"} | {d["modules"]} | {int(s//60)}m {s%60:.2f}s ({s:.2f} s) | {d["peak_aggregate_compiler_rss_bytes"]/2**30:.3f} GiB | {d["peak_single_compiler_rss_bytes"]/2**30:.3f} GiB |')
lines += ['',f'LeanPool took **{comparison["leanpool_wall_reduction_percent"]:.1f}% less wall time**',
    f'(**{comparison["oai_wall_divided_by_leanpool"]:.2f}× speedup**) and used',
    f'**{comparison["leanpool_aggregate_rss_reduction_percent"]:.1f}% less peak aggregate compiler RSS**.', '',
    'These are one clean source build per variant, with precompiled shared dependencies.',
    'LeanPool ran first, OAI second. The OS filesystem cache was not flushed; no claim',
    'of a cold-disk benchmark or statistical confidence interval is made.',
    'The first LeanPool attempt was labeled `preflight`; it completed as a full clean',
    'build without source repairs or retries, so its recorded measurements are used.', '',
    'Aggregate RSS is sampled every 50 ms and counts shared resident pages separately',
    'in each process. Peak single-process RSS is the exact macOS `wait4` high-water',
    'mark. The Python scheduler is excluded from both RSS measures.', '',
    'Scope: the complete dependency closure of the two final NS breakdown theorems',
    '(whole space and periodic). Ancillary paper results and standalone Euler targets',
    'are excluded. Dependency downloads and cache preparation are outside timing.', '',
    f'Raw results: [`{a.oai}`]({a.oai}/summary.json), [`{a.leanpool}`]({a.leanpool}/summary.json).',
    'Per-module commands, timings, RSS, source hashes, compiler logs, and RSS time series',
    'are preserved alongside each summary. See [README](../README.md) for reproduction.', '']
(ROOT/'results/REPORT.md').write_text('\n'.join(lines))
print('\n'.join(lines))
