import NavierStokes.ActualCycleParameters
import NavierStokes.CyclePhysicalPrefixes
import NavierStokes.CycleStateCoherence
import NavierStokes.ActualInitialMeanEquation
import NavierStokes.ActualIterationLedger
import NavierStokes.ActualCarrierGeometry
import NavierStokes.ActualMeanPhysicalData
import NavierStokes.ActualMeanStageData
import NavierStokes.MixedCandidateAssembly
import NavierStokes.ActualCandidateConstruction

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
  -- #check NavierStokes.ActualCandidateConstruction.meanField B N0 degree (f + g) w =
  -- (NavierStokes.ActualCandidateConstruction.meanField B N0 degree f +
  --     NavierStokes.ActualCandidateConstruction.meanField B N0 degree g)
  --   w =?= (NavierStokes.ActualCandidateConstruction.meanAtlas B N0).physical
  --   NavierStokes.CorrectionInitialization.ActualPrimary.standardRegion.carrier degree (f + g)
  --   (NavierStokes.PhysicalMeanJetBounds.physicalPoint NavierStokes.CorrectionInitialization.ActualPrimary.h w) =
  -- ((NavierStokes.ActualCandidateConstruction.meanAtlas B N0).physical
  --       NavierStokes.CorrectionInitialization.ActualPrimary.standardRegion.carrier degree f +
  --     (NavierStokes.ActualCandidateConstruction.meanAtlas B N0).physical
  --       NavierStokes.CorrectionInitialization.ActualPrimary.standardRegion.carrier degree g)

  exact congrFun ((meanAtlas B N0).physical_add standardRegion.carrier degree f g)
    (PhysicalMeanJetBounds.physicalPoint h w)

-- #check NavierStokes.ActualCandidateConstruction.meanField B N0 degree (f + g) w =
--   (NavierStokes.ActualCandidateConstruction.meanField B N0 degree f +
--       NavierStokes.ActualCandidateConstruction.meanField B N0 degree g)
--     w =?= (NavierStokes.ActualCandidateConstruction.meanAtlas B N0).physical
--     NavierStokes.CorrectionInitialization.ActualPrimary.standardRegion.carrier degree (f + g)
--     (NavierStokes.PhysicalMeanJetBounds.physicalPoint NavierStokes.CorrectionInitialization.ActualPrimary.h w) =
--   ((NavierStokes.ActualCandidateConstruction.meanAtlas B N0).physical
--         NavierStokes.CorrectionInitialization.ActualPrimary.standardRegion.carrier degree f +
--       (NavierStokes.ActualCandidateConstruction.meanAtlas B N0).physical
--         NavierStokes.CorrectionInitialization.ActualPrimary.standardRegion.carrier degree g)
