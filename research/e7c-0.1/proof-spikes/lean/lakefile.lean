import Lake
open Lake DSL

package "e7cProofSpike" where
  version := v!"0.1.0"

@[default_target]
lean_lib E7CProofSpike
