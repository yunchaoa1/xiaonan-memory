```yaml
blockage:
  blockage_id: BLK-001
  code: empty_input
  message: "customer_idea 为空字符串，未形成任何可用于小说创作的非空语义单元；本次运行按契约阻断，且不生成小说。"
  trigger_refs:
    - SRC-USER-001
  violated_lock_refs: []
  recoverability: new_request_required
  question_asked: false

provenance_and_decisions:
  schema_version: opc-writing-pad/0.3-test
  run_status: blocked
  input_state:
    status: blocked
    missing_fields:
      - customer_idea.nonempty_semantic_unit
    conflicting_refs: []
    resolution_item_refs:
      - PAD-001
      - PAD-002
    question_asked: false
  items:
    - item_id: PAD-001
      kind: decision
      statement: "固定输入 customer_idea 为空字符串，依据空输入阻断规则选择 blocked 分支，不进入小说生成路径。"
      source_ref: SRC-USER-001
      body_ref: NONE
      rule_ref: RULE-BLOCK-EMPTY-INPUT
      status: adopted
      related_refs:
        - BLK-001
    - item_id: PAD-002
      kind: risk
      statement: "输入不含小说语义单元；若继续生成将构成无来源创意事实与伪造小说交付。"
      source_ref: SRC-USER-001
      body_ref: GLOBAL
      rule_ref: LOCK-RUNTIME-EXTERNAL-CREATIVE-SOURCE
      status: triggered
      related_refs:
        - PAD-001
        - BLK-001
  divergence_record:
    record_mode: concise_audit_not_chain_of_thought
    paths: []
    selected_path_id: NONE
    selected_path_count: 0
    external_candidate_bodies: 0
  hard_gate_results: []
  first_delivery_usability_result:
    contract_version: opc-writing-first-delivery/0.5-test
    status: not_applicable_blocked
    customer_submission_count: 1
    customer_midprocess_intervention_count: 0
    exposed_internal_draft_count: 0
    first_external_novel_count: 0
    hard_gate_result_refs: []
    all_six_logic_gates_pass: false
    first_external_artifact_ref: NONE
    customer_post_delivery_editing_allowed: true
    evidence_refs:
      - SRC-USER-001
      - BLK-001
  downstream_handoff:
    handoff_schema_version: opc-writing-handoff/0.3-test
    availability: blocked
    novel_id: null
    novel_version: null
    body_refs: []
    facts: []
    characters: []
    relationships: []
    world_rules: []
    timeline: []
    causal_chains: []
    setups_and_payoffs: []
    chapter_boundaries: []
    provenance_item_refs:
      - PAD-001
      - PAD-002
    hard_gate_result_refs: []
    known_risk_refs:
      - PAD-002
    blockage_ref: BLK-001
    allowed_downstream_sources:
      - this_novel_version
      - this_provenance_and_decisions
      - accepted_upstream_artifacts
      - downstream_validated_locked_rules
    forbidden_downstream_sources:
      - customer_chat_supplement
      - history
      - network
      - oral_explanation
      - other_projects
      - internal_candidate_paths
      - unaccepted_drafts
      - production_distillation_material
  regression_fixture:
    fixture_schema_version: opc-writing-regression/0.5-test
    fixture_set_id: FIXSET-WRITING-ENTRY-005
    immutable: true
    execution_status: executed
    pass_claim_allowed_without_artifacts: false
    required_case_result_fields:
      - case_id
      - execution_status
      - output_branch
      - assertion_results
      - artifact_refs
      - verifier_ref
    cases:
      - case_id: FIX-BLOCKED-001
        execution_status: executed
        output_branch: blocked
        input_payload:
          customer_idea: ""
        assertion_results:
          - assertion: run_status_is_blocked
            observed: true
            evidence_refs: [BLK-001, PAD-001]
          - assertion: blockage_schema_complete
            observed: true
            evidence_refs: [BLK-001]
          - assertion: novel_key_absent
            observed: true
            evidence_refs: [BLK-001]
          - assertion: body_cardinality_zero
            observed: true
            evidence_refs: [BLK-001]
          - assertion: question_asked_false
            observed: true
            evidence_refs: [BLK-001, PAD-001]
          - assertion: exact_blocked_top_level_keys
            observed: true
            observed_value: [blockage, provenance_and_decisions]
            evidence_refs: [BLK-001]
          - assertion: customer_submission_count_equals_one
            observed: true
            observed_value: 1
            evidence_refs: [SRC-USER-001]
          - assertion: customer_midprocess_intervention_count_equals_zero
            observed: true
            observed_value: 0
            evidence_refs: [PAD-001]
          - assertion: exposed_internal_draft_count_equals_zero
            observed: true
            observed_value: 0
            evidence_refs: [PAD-001]
          - assertion: first_external_novel_count_equals_blocked_zero
            observed: true
            observed_value: 0
            evidence_refs: [BLK-001]
          - assertion: first_delivery_usability_uses_blocked_fixed_values
            observed: true
            observed_value:
              status: not_applicable_blocked
              hard_gate_result_refs: []
              all_six_logic_gates_pass: false
              first_external_artifact_ref: NONE
            evidence_refs: [BLK-001]
          - assertion: downstream_handoff_availability_is_blocked
            observed: true
            observed_value: blocked
            evidence_refs: [BLK-001]
          - assertion: downstream_blockage_ref_matches_top_level
            observed: true
            observed_value: BLK-001
            evidence_refs: [BLK-001]
          - assertion: no_independent_pass_claim
            observed: true
            observed_value: "仅记录本次运行的同执行者结构化自检；未进行独立核验，不构成独立 PASS、验收通过或能力验证声明。"
            evidence_refs: [PAD-001]
        artifact_refs:
          - result.md
        verifier_ref: SELF-CHECK-FIX-BLOCKED-001-NON-INDEPENDENT
        verification_scope: same-runner_structural_self_check_only
        independent_verification_performed: false
        independent_pass_claim: false
```
