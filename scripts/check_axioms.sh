#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
for variant in oai leanpool; do
  if [ "$variant" = oai ]; then module=NavierStokes.ComparatorSolution
  else module=LeanPool.NavierStokesAndEuler.NavierStokes.ComparatorSolution; fi
  printf 'import %s\n#print axioms NavierStokes.Comparator.navier_stokes_breakdown_R3\n#print axioms NavierStokes.Comparator.navier_stokes_breakdown_periodic\n' "$module" > "$variant/CheckAxioms.lean"
  (cd "$variant" && lake env lean -j1 CheckAxioms.lean) > "results/$variant-axioms.log" 2>&1
  rm "$variant/CheckAxioms.lean"
done
