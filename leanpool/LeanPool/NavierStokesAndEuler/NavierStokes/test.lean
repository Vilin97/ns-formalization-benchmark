import LeanPool.NavierStokesAndEuler.NavierStokes.ActualCandidateAssembly

namespace NavierStokes.ActualCandidateConstruction

open Set Function Filter ProblemStatement
open CorrectionState CorrectionStep
open CorrectionInitialization.ActualPrimary
open scoped ContDiff Topology BigOperators


-- set_option diagnostics true in
-- set_option diagnostics.threshold 100 in
theorem meanField_add' (B N0 : ℕ) (degree : ℝ) (f g : ActualMeanPhysicalData.Scalar) :
    meanField B N0 degree (f + g) = meanField B N0 degree f + meanField B N0 degree g := by
  funext w
  exact congrFun ((meanAtlas B N0).physical_add standardRegion.carrier degree f g)
    (PhysicalMeanJetBounds.physicalPoint h w)
