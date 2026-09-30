import E7CJointGraphBytecodeSyntax

/- Generated from the checked live unspecialized CPython-3.12 _graph
image. CACHE entries are recorded separately. Dispatch adequacy is
not established by this program or its all-input theorem. -/
namespace E7CJointGraphBytecodeGenerated
open E7CJointGraphBytecodeSyntax

def graphProgram : List Instruction :=
  [(.resume 0),
   (.loadGlobal "list" true),
   (.loadFast 0),
   (.loadAttr "edges"),
   (.call 1),
   (.loadFast 0),
   (.loadAttr "tag"),
   (.loadKeys ["edges", "tag"]),
   (.buildConstKeyMap 2),
   .returnValue]

end E7CJointGraphBytecodeGenerated
