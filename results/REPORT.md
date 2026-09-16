# Local compilation results

Both builds completed successfully with the exact same Lean 4.34.0-rc2 compiler
and Mathlib dependencies on this Apple M4 Pro laptop (12 cores, 48 GiB RAM, macOS 15.7.4).
Four concurrent compiler processes, one Lean worker thread per process.

| Version | Modules | Wall time | Peak aggregate compiler RSS | Peak single compiler RSS |
|---|---:|---:|---:|---:|
| OAI original | 580 | 18m 4.27s (1084.27 s) | 13.273 GiB | 5.845 GiB |
| LeanPool | 422 | 11m 11.04s (671.04 s) | 6.451 GiB | 2.196 GiB |

LeanPool took **38.1% less wall time**
(**1.62× speedup**) and used
**51.4% less peak aggregate compiler RSS**.

These are one clean source build per variant, with precompiled shared dependencies.
LeanPool ran first, OAI second. The OS filesystem cache was not flushed; no claim
of a cold-disk benchmark or statistical confidence interval is made.
The first LeanPool attempt was labeled `preflight`; it completed as a full clean
build without source repairs or retries, so its recorded measurements are used.

Aggregate RSS is sampled every 50 ms and counts shared resident pages separately
in each process. Peak single-process RSS is the exact macOS `wait4` high-water
mark. The Python scheduler is excluded from both RSS measures.

Scope: the complete dependency closure of the two final NS breakdown theorems
(whole space and periodic). Ancillary paper results and standalone Euler targets
are excluded. Dependency downloads and cache preparation are outside timing.

Raw results: [`oai-run1`](oai-run1/summary.json), [`leanpool-preflight`](leanpool-preflight/summary.json).
Per-module commands, timings, RSS, source hashes, compiler logs, and RSS time series
are preserved alongside each summary. See [README](../README.md) for reproduction.
