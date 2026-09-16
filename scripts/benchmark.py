#!/usr/bin/env python3
"""Build the final NS theorem closure with bounded, identical Lean concurrency.

Dependencies must already be cached. Each successful module emits a fresh olean.
RSS is the sum of resident sets of active compiler processes, sampled every 50 ms;
shared pages are counted once per process. wait4 also captures exact per-process
peak RSS (bytes on macOS). No Lake scheduling/cache checks enter the timed region.
"""
import argparse, hashlib, json, os, platform, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import psutil

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {'oai': 'NavierStokes.ComparatorSolution', 'leanpool': 'LeanPool.NavierStokesAndEuler.NavierStokes.ComparatorSolution'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=TARGETS)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--label', default='run1')
    parser.add_argument('--resume', action='store_true', help='Diagnostic only: reuse successful modules; not a clean benchmark')
    args = parser.parse_args()
    project = ROOT / args.variant
    output = ROOT / 'results' / f'{args.variant}-{args.label}'
    output.mkdir(parents=True, exist_ok=False)
    build = project / '.lake/build/lib/lean'
    if not args.resume and build.exists(): shutil.rmtree(build)
    build.mkdir(parents=True, exist_ok=True)
    env = json.loads(subprocess.check_output(['lake', 'env', sys.executable, '-c', 'import os,json; print(json.dumps(dict(os.environ)))'], cwd=project))
    lean = subprocess.check_output(['lake', 'env', 'which', 'lean'], cwd=project, text=True).strip()
    version = subprocess.check_output([lean, '--version'], text=True).strip()
    sources = {str(p.relative_to(project))[:-5].replace('/', '.'): p for p in project.rglob('*.lean') if '.lake' not in p.parts}
    graph = {}
    def visit(module):
        if module in graph: return
        imports = []
        for line in sources[module].read_text().splitlines():
            m = re.match(r'\s*(?:public |private )?import (.*)', line)
            if m: imports.extend(x for x in m[1].split('--')[0].split() if x in sources)
        graph[module] = set(imports)
        for dep in imports: visit(dep)
    visit(TARGETS[args.variant])
    meta = {'variant': args.variant, 'label': args.label, 'jobs': args.jobs, 'lean_threads': 1,
            'lean': version, 'lean_binary': lean, 'platform': platform.platform(),
            'started_utc': datetime.now(timezone.utc).isoformat(), 'clean': not args.resume,
            'modules': len(graph), 'rss_sample_interval_seconds': 0.05,
            'source_sha256': {m: hashlib.sha256(sources[m].read_bytes()).hexdigest() for m in sorted(graph)}}
    (output/'metadata.json').write_text(json.dumps(meta, indent=2)+'\n')
    done = {m for m in graph if args.resume and (build / (m.replace('.', '/')+'.olean')).exists()}
    pending = set(graph) - done; running = {}; records = []; failed = []
    peak_rss = 0; peak_process = 0; start = time.perf_counter()
    with (output/'rss.csv').open('w') as samples:
        samples.write('elapsed_seconds,aggregate_compiler_rss_bytes,active_compilers\n')
        while pending or running:
            if not failed:
                ready = sorted(m for m in pending if graph[m] <= done)
                for module in ready[:max(0,args.jobs-len(running))]:
                    target = build / (module.replace('.', '/')+'.olean'); target.parent.mkdir(parents=True, exist_ok=True)
                    log = (output / (module+'.log')).open('w')
                    command = [lean, '-j1', '-o', str(target), str(sources[module].relative_to(project))]
                    proc = subprocess.Popen(command, cwd=project, env=env, stdout=log, stderr=subprocess.STDOUT)
                    running[proc.pid] = (proc, module, log, time.perf_counter(), command)
                    pending.remove(module)
            rss = 0
            for pid, (proc, module, log, began, command) in list(running.items()):
                try: rss += psutil.Process(pid).memory_info().rss
                except psutil.NoSuchProcess: pass
                waited, status, usage = os.wait4(pid, os.WNOHANG)
                if not waited: continue
                proc.returncode = os.waitstatus_to_exitcode(status)
                log.close()
                maxrss = usage.ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
                peak_process = max(peak_process, maxrss)
                records.append({'module': module, 'wall_seconds': time.perf_counter()-began,
                                'peak_rss_bytes': maxrss, 'exit_code': proc.returncode, 'command': command})
                del running[pid]
                if proc.returncode == 0: done.add(module)
                else: failed.append(module)
                print(f'{args.variant}: {len(done)}/{len(graph)} {module}: exit {proc.returncode}, {records[-1]["wall_seconds"]:.1f}s', flush=True)
                (output/'modules.json').write_text(json.dumps(records, indent=2)+'\n')
            peak_rss = max(peak_rss, rss)
            samples.write(f'{time.perf_counter()-start:.3f},{rss},{len(running)}\n'); samples.flush()
            if failed and not running: break
            if pending and not running and not any(graph[m] <= done for m in pending): raise RuntimeError('Dependency cycle')
            if pending or running: time.sleep(0.05)
    result = {**{k:v for k,v in meta.items() if k != 'source_sha256'}, 'wall_seconds': time.perf_counter()-start,
              'peak_aggregate_compiler_rss_bytes': peak_rss, 'peak_single_compiler_rss_bytes': peak_process,
              'completed_modules': len(done), 'failed_modules': failed, 'success': len(done)==len(graph)}
    (output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    return 0 if result['success'] else 1

if __name__ == '__main__': raise SystemExit(main())
