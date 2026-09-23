import LeanPool.NavierStokesAndEuler.NavierStokes.ActualCandidateAssembly
import Mathlib.Util.CountHeartbeats

open NavierStokes
open NavierStokes.ActualCandidateConstruction
open NavierStokes.CorrectionInitialization.ActualPrimary
set_option diagnostics true
set_option diagnostics.threshold 100
set_option profiler true
set_option profiler.threshold 1

#count_heartbeats in
example (B N0 : ℕ) (degree : ℝ) (f g : ActualMeanPhysicalData.Scalar) :
    meanField B N0 degree (f + g) = meanField B N0 degree f + meanField B N0 degree g := by
  funext w
  exact congrFun ((meanAtlas B N0).physical_add standardRegion.carrier degree f g)
    (PhysicalMeanJetBounds.physicalPoint h w)

#count_heartbeats in
example (B N0 : ℕ) (degree : ℝ) (f g : ActualMeanPhysicalData.Scalar) :
    meanField B N0 degree (f + g) = meanField B N0 degree f + meanField B N0 degree g := by
  funext w
  dsimp only [meanField, Function.comp_apply, Pi.add_apply]
  exact congrFun ((meanAtlas B N0).physical_add standardRegion.carrier degree f g)
    (PhysicalMeanJetBounds.physicalPoint h w)

#count_heartbeats in
example (B N0 : ℕ) (degree : ℝ) (f g : ActualMeanPhysicalData.Scalar) :
    meanField B N0 degree (f + g) = meanField B N0 degree f + meanField B N0 degree g := by
  funext w
  simpa only [meanField, Function.comp_apply, Pi.add_apply] using
    congrFun ((meanAtlas B N0).physical_add standardRegion.carrier degree f g)
      (PhysicalMeanJetBounds.physicalPoint h w)
