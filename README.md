# Navier–Stokes: OAI vs LeanPool

Separate local builds of the original OpenAI formalization and its LeanPool
version, with the exact same Lean compiler, Mathlib revision and compiler concurrency.

## Sources and scope

- **OAI**: [OpenAI's original September 8 release](https://github.com/openai/NavierStokesAndEuler/tree/8937a8f4cbc7abaab5e9e97d1cc7f5d2319d9538).
- **LeanPool**: [snapshot bb74ee0](https://github.com/Vilin97/lean-pool/tree/bb74ee07fc23bc81358d75a9c40303e5e27fced8).
  LeanPool's project metadata explicitly identifies the OAI commit above as its source.
- Each directory contains the complete transitive source dependency closure of
  `NavierStokes.ComparatorSolution` (under `LeanPool.NavierStokesAndEuler` in
  LeanPool). Both targets prove `NavierStokes.Comparator.navier_stokes_breakdown_R3`
  and `NavierStokes.Comparator.navier_stokes_breakdown_periodic`.
- Euler modules are included only when required by these NS targets. Unrelated
  Euler results, comparator tooling, and ancillary paper results are excluded.
- Original build configurations, module lists, and SHA-256 source hashes are in
  `upstream/`. Sources retain their upstream paths and licensing.

## Common environment

- Lean **4.34.0-rc2**; toolchain `leanprover/lean4:v4.34.0-rc2`.
- Mathlib **85e3a25e006c35636f0e53b0e9296caca2685bc0**, with identical transitive
  dependencies locked in both `lake-manifest.json` files.
- Four concurrent compiler processes, each invoked with `lean -j1`.
- Same default Lean options for both versions; source-local options retained.
- macOS laptop: Apple M4 Pro, 12 CPU cores, 48 GiB RAM, AC power.

## Reproduce

Install elan and Python 3, then:

```sh
./scripts/setup.sh
.venv/bin/python scripts/benchmark.py leanpool --label run1
.venv/bin/python scripts/benchmark.py oai --label run1
```

Run variants sequentially. Labels must be new; existing results are never overwritten.
For an ordinary Lake build, use `cd oai && lake build`, or
`cd leanpool && lake build`. The measured runner invokes the same Lean compiler
directly in each package's Lake environment, ordering modules by imports and
writing `.olean` files to each package's separate `.lake/build/lib/lean` directory.
It does not produce native object files or executables.

Every measured clean run removes that variant's existing project `.olean` outputs.
Downloaded and compiled Mathlib dependencies are shared and excluded from timing.
The filesystem cache is not flushed. The timer includes scheduling, compiler
startup, elaboration, kernel checking, and `.olean` serialization for the entire
NS target closure. Environment setup and dependency fetching are outside timing.

`peak_aggregate_compiler_rss_bytes` sums the RSS of active Lean compiler processes,
sampled every 50 ms. This is resident-set accounting: shared pages are counted
in each process and brief peaks between samples may be missed. The Python
scheduler is excluded. `peak_single_compiler_rss_bytes` is the largest exact
per-process high-water mark from macOS `wait4`, whose `ru_maxrss` unit is bytes.
Do not interpret `/usr/bin/time -l`'s maximum child RSS as aggregate parallel memory.

Every run saves metadata, the exact compiler commands, per-module elapsed times
and peak RSS, compiler logs, RSS samples, and a summary under `results/`.
`--resume` is only for diagnosing compatibility errors; its timing is not a clean
benchmark and must not be compared against full runs.

## Results

Both builds succeeded, with **no edits to either version's Lean source files**.
Only the build configurations and LeanPool's Lean/Mathlib pins changed.

| Version | Wall time | Peak aggregate compiler RSS | Peak single compiler RSS |
|---|---:|---:|---:|
| OAI original (580 modules) | 18m 4.27s | 13.273 GiB | 5.845 GiB |
| LeanPool (422 modules) | 11m 11.04s | 6.451 GiB | 2.196 GiB |

LeanPool was **1.62× faster** (38.1% less wall time) and used **51.4% less peak
aggregate compiler RSS** in these single clean builds. See the
[full report](results/REPORT.md), [machine details](results/machine.json), and
[raw comparison](results/comparison.json).

The first successful clean LeanPool run is named `leanpool-preflight`; it did
not require repairs or a resumed build. OAI ran after LeanPool. Common dependency
cache preparation is excluded from both measurements; OS filesystem caches were
not flushed.

## Verification and compatibility

LeanPool's Lean/Mathlib 4.34.0-rc1 pins were replaced by the common OAI 4.34.0-rc2
pins. Package configurations were narrowed to the matching final NS theorems.
Proof files match their pinned upstream SHA-256 hashes byte for byte; run
`.venv/bin/python scripts/verify_sources.py` to check this.

Both final theorem pairs were separately inspected with `#print axioms` after
compilation. Only `propext`, `Classical.choice`, and `Quot.sound` occur; there is
no `sorryAx`. The logs are in `results/oai-axioms.log` and
`results/leanpool-axioms.log`. This checks axiom dependencies, not independent
semantic equivalence to the informal mathematical statement.

```sh
./scripts/check_axioms.sh
.venv/bin/python scripts/summarize.py
```

## Profile a directory with Lean's profiler

From this repository's root:

```sh
python3 scripts/profile_directory.py \
  leanpool/LeanPool/NavierStokesAndEuler/NavierStokes \
  --output results/ns-profile
```

The script finds the enclosing Lake project and runs
`lake env lean --profile <file>` sequentially for every `.lean` file, recursively.
It uses exactly those Lean flags, preserving the behavior of the single-file
command. Imports must already be built; this is profiling, not a clean rebuild.
Dependency caches (`.lake`) and Git internals are excluded.

The output directory contains:

- `REPORT.md`: per-file table, sorted by wall time, with import, elaboration,
  type checking and tactic timings, plus success/failure status.
- `summary.csv`: per-file wall time and **all** cumulative phase timings Lean reports.
- `events.csv`: individual `... took ...` timings reported by Lean.
- `results.json`, `metadata.json`, and `logs/`: structured results, commands,
  input file list, and complete profiler output.

Wall time includes Lake startup. Cumulative profiler categories exclude nested
profiled work, but their sum need not equal wall time because of parallel tasks
and unprofiled work. Individual events also contribute to the cumulative totals;
do not add the events to those totals. Missing phases remain blank, not zero.
Reports are checkpointed after each file. Failures remain in the table, the
remaining files still run, and the script exits nonzero if any file failed.

A single file also works. Use `--no-recursive` for immediate children only,
`--project PATH` to explicitly choose the Lake project, and `--timeout SECONDS`
to limit each file. An existing output directory is never overwritten; omit
`--output` for a new timestamped directory under `./profile-results/`.

An example directory run is saved in
[results/profile-for-mathlib/REPORT.md](results/profile-for-mathlib/REPORT.md).
