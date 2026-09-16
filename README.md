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

## Compatibility changes and results

Build configuration changes: LeanPool's Lean/Mathlib 4.34.0-rc1 pins are replaced
by the common OAI 4.34.0-rc2 pins. Package configurations are narrowed to the two
matching final theorems. Source changes and measured results will be recorded
here after successful builds.
