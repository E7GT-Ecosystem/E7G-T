# MSC/0.1 review resolution

**Reviewed head:** `0dcedd07a527fe629ef297e19b363a686185d980`  
**Disposition at reviewed head:** material revision required  
**Revision target:** PR #32, research proposal only

The originating author found the mathematical purpose preserved and accepted
the `MSC/0.1 — Multi-Scope Coherence` name, common-codomain span, compatible
family, parity obstruction, access/retention/authority separation and the
separation of compositional extensions. The ecosystem review agreed with the
research direction but identified admission and semantic defects. This record
maps those findings to the revised package.

| Finding | Resolution | Regression evidence |
| --- | --- | --- |
| Scope order underdefined | `MSC.1` now defines `preceq` as the reflexive-transitive closure of the finite acyclic link graph; evaluator emits that closure. | `test_unique_closure`, `test_scope_cycle_rejected` |
| Partial coherence-map mismatch | Abstract profile defines jointly evaluable assignments for partial maps; MSC-B1 explicitly requires total-on-admitted-carrier coherence maps. | `test_partial_required_map_is_unsupported` |
| Schema/runtime admission divergence | Dependency-free runtime now enforces required/additional fields, identifier uniqueness, carrier/map types and every optional reference before evaluation outcomes. | `test_additional_schema_field_rejected_at_runtime` and malformed-reference tests |
| Invalid optional references hidden by resource limit | All access, invariant, commutation and reconstruction declarations are admitted before combination counting. | `test_invalid_access_reference_not_hidden_by_resource_limit`, `test_invalid_invariant_reference_not_hidden_by_resource_limit` |
| Non-object JSON traceback | Root admission requires an object and CLI returns controlled exit code 2. | `test_non_object_roots_are_controlled_validation_errors`, `test_cli_non_object_roots_exit_two_without_traceback` |
| Unknown/duplicate optional identifiers | Unknown map references and duplicate profile/test IDs are malformed input, not `unsupported` capability. | `test_unknown_commutation_reference_is_malformed`, `test_duplicate_optional_identifiers_rejected` |
| Vacuous invariant wording | Empty global closure now reports `not_applicable_incompatible`; it never reports preservation. | `test_invariant_on_incompatible_family_is_not_applicable` |
| Partial invariant semantics | Extractors must be defined on every selected state in every compatible family; undefined unreachable states are permitted. | two partial-invariant tests |
| Undefined coordinate projection | `MSC.8` defines coordinate projection, scope-state fibre and observation fibre separately; evaluator supports both query kinds. | `test_scope_state_and_observation_fibres_are_distinct` |
| “Pairwise” ambiguous | Normative term is now `link-wise satisfiability`, explicitly limited to independent declared links. | obstruction fixture and `test_pairwise_compatible_global_obstruction` |
| Empty observation family | Defined as universal indistinguishability and one quotient class. | `test_empty_observation_family_is_universal_quotient` |
| `C_e` terminology | `C_e` is the lower-scope comparison map; bridge means the whole span. Schema field is `comparison_map`. | schema and both fixtures |
| Non-native boundary vocabulary | Replaced with model-independent truth, external system existence and externally instantiated scope hierarchy. | textual review |

## Remaining gates

This resolution is first-party work and does not claim that the reviewers have
accepted the changes. Before merge, the revised commit should receive:

1. originating-author re-review;
2. ecosystem/formal re-review;
3. visible GitHub Actions execution; and
4. confirmation that no blocking or material findings remain.

Independent reimplementation and a substantive example remain gates for any
future promotion beyond `proposals/msc-0.1`.

## Re-review request

Please review the revised PR #32 against the finding table above. For every
row, return `resolved`, `partially_resolved`, or `unresolved`, with an exact
replacement where further change is required. Conclude with one verdict:

- `ready_to_merge_as_research_proposal`;
- `minor_corrections_before_merge`; or
- `material_revision_still_required`.

