import Lake
open Lake DSL

package "e7cLeanCore" where
  version := v!"0.1.0"

lean_lib E7CS1StrictCore

@[default_target]
lean_lib E7CLeanCore
