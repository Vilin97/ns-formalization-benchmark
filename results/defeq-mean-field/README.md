# Definitional-equality example: meanField_add

Measured on 2026-09-23 with the repository's Lean 4.34.0-rc2 toolchain.
The source snapshots and benchmark source files have not been changed.

Source declarations:
- OAI: `oai/NavierStokes/ActualCandidateConstruction.lean:368`
- LeanPool: `leanpool/LeanPool/NavierStokesAndEuler/NavierStokes/ActualCandidateAssembly.lean:435`

Both contain the same short proof. Isolated copies of the theorem in
`oai/DefeqProbe.lean` and `leanpool/DefeqProbe.lean` compare the original proof
with two equivalent proofs that make wrapper reduction explicit.

| Variant | Original | Add dsimp only | simpa only variant |
|---|---:|---:|---:|
| OAI | 88,967 | 83 | 147 |
| LeanPool | 396 | 83 | 148 |

Values are Lean `#count_heartbeats` reports for each isolated declaration, not
wall-clock speedup factors or whole-project costs. Imports are not part of these
per-declaration heartbeat counts. Three examples are checked in order in each
probe: original, dsimp only, simpa only. All six compiled successfully.

The one-line change is to insert after `funext w`:

```lean
dsimp only [meanField, Function.comp_apply, Pi.add_apply]
```

This aligns the goal with the generic `Atlas.physical_add` theorem before the
`exact congrFun ...` step. The original OAI proof reports 193,536 unfoldings of
`Nat.rec`, 342,180 of `Nat.casesOn`, and 55,296 of `Classical.choose` in the meta
reduction diagnostics. These are unnecessary for transferring additivity through
function composition. Those large counters disappear in the explicit-wrapper
variant (reporting threshold 100). The kernel's small remaining reduction counts
are distinct from these elaborator counters.

LeanPool's original proof is already much less expensive despite identical proof
text; this experiment does not isolate which upstream definition changes account
for that difference.

Reproduce from the repository root:

```sh
(cd oai && lake env lean -j1 --json DefeqProbe.lean)
(cd leanpool && lake env lean -j1 --json DefeqProbe.lean)
```

The raw diagnostic and profiler output is preserved in `oai.log` and `leanpool.log`.
