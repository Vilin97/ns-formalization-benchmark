# Lean directory profile

Times in seconds; sorted by wall time, slowest first. Files run sequentially.
Wall time includes Lake startup. Cumulative phase times exclude nested profiled work.
Phase totals need not equal wall time (parallel tasks and unprofiled work). A dash means an unreported phase. Full phase data is in `summary.csv`.

| File | Wall | Import | Elaboration | Type checking | Tactics | Status |
|---|---:|---:|---:|---:|---:|---|
| LeanPool/NavierStokesAndEuler/NavierStokes/ActualSignedCurrentSupport.lean | 4.175 | 1.890 | 0.055 | 0.021 | 0.029 | ok |

Files completed: 1. Sum of per-file wall times: 4.175 s.
This profiles existing source files using already-built imports; it does not rebuild dependencies.
