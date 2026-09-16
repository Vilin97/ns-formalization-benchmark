# Lean directory profile

Times in seconds; sorted by wall time, slowest first. Files run sequentially.
Wall time includes Lake startup. Phase times can overlap; do not sum them.
A dash means Lean did not report that phase. Full phase data is in `summary.csv`.

| File | Wall | Import | Elaboration | Type checking | Tactics | Status |
|---|---:|---:|---:|---:|---:|---|
| LeanPool/NavierStokesAndEuler/ForMathlib/SobolevThreeDimensional.lean | 4.641 | 1.690 | 0.103 | 0.140 | 0.310 | ok |
| LeanPool/NavierStokesAndEuler/ForMathlib/SmoothCutoff.lean | 3.990 | 1.540 | 0.080 | 0.079 | 0.095 | ok |
| LeanPool/NavierStokesAndEuler/ForMathlib/Gronwall.lean | 3.487 | 1.360 | 0.021 | 0.027 | 0.057 | ok |
| LeanPool/NavierStokesAndEuler/ForMathlib/FiniteDimensionalBumps.lean | 3.400 | 1.580 | 0.002 | 0.001 | 0.000 | ok |
| LeanPool/NavierStokesAndEuler/ForMathlib/StronglyMeasurable.lean | 3.388 | 1.220 | 0.002 | 0.000 | 0.001 | ok |
| LeanPool/NavierStokesAndEuler/ForMathlib/WeightedDecay.lean | 3.140 | 0.971 | 0.005 | 0.002 | 0.007 | ok |
| LeanPool/NavierStokesAndEuler/ForMathlib/SmoothnessOrder.lean | 2.453 | 0.441 | 0.002 | 0.001 | 0.001 | ok |

Files completed: 7. Sum of per-file wall times: 24.498 s.
This profiles existing source files using already-built imports; it does not rebuild dependencies.
