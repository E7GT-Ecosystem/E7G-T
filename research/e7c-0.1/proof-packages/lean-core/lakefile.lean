import Lake
open Lake DSL

package "e7cLeanCore" where
  version := v!"0.1.0"

lean_lib E7CS1StrictCore
lean_lib E7CS1FG3Single
lean_lib E7CS1FG3Rows
lean_lib E7CS1ExactCollect
lean_lib E7CS1FG3Codec
lean_lib E7CS1RatArithmetic

@[default_target]
lean_lib E7CLeanCore
