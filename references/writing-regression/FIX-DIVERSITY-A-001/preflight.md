# FIX-DIVERSITY-A-001 写前预检

```yaml
fixture:
  case_id: FIX-DIVERSITY-A-001
  skill_version: 0.5.1-test
  phase: preflight_only
  novel_body_count: 0
  external_candidate_body_count: 0
  customer_midprocess_intervention_count: 0

source_isolation:
  runtime_external_creative_source: SRC-USER-001_only
  history_read: false
  network_read: false
  other_project_material_read: false
  historical_sample_read: false
  internal_candidate_bodies_exposed: false
  forbidden_sources:
    - customer_chat_supplement
    - history
    - network
    - other_projects
    - historical_samples
    - internal_candidate_paths
    - unaccepted_drafts

locked_customer_facts:
  - fact_id: FACT-001
    source_ref: SRC-USER-001
    statement: 主角关系由两位退休厨师构成。
    status: locked
  - fact_id: FACT-002
    source_ref: SRC-USER-001
    statement: 两人曾经是朋友，故事目标是让他们重新成为朋友。
    status: locked
  - fact_id: FACT-003
    source_ref: SRC-USER-001
    statement: 关系修复围绕一道失传家常菜展开。
    status: locked
  - fact_id: FACT-004
    source_ref: SRC-USER-001
    statement: 类型为 warm_comedy（温暖喜剧）。
    status: locked
  - fact_id: FACT-005
    source_ref: SRC-USER-001
    statement: 节奏为 slow_burn（慢燃）。
    status: locked

creative_guardrails:
  preserve_requested_taste: true
  force_power_fantasy: false
  force_revenge: false
  force_conspiracy: false
  force_noir_or_darkening: false
  statement: 不强行爽文、复仇、阴谋或黑色化；冲突保持日常、低烈度、人物选择驱动，喜剧不消解真情。

divergence_record:
  record_mode: concise_audit_not_chain_of_thought
  selected_path_count: 1
  selected_path_id: PATH-001
  external_candidate_bodies: 0
  paths:
    - path_id: PATH-001
      status: selected
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 两位退休厨师因共同追索失传家常菜的味道，被迫在买菜、试做、争论旧手法和照顾彼此体力的日常协作中重新磨合；误差与嘴硬制造温暖喜剧，真正的回报是承认当年的伤害并恢复平等友谊。
      selection_reason: 最贴合温暖喜剧与慢燃承诺，核心进展来自两人的主动选择，不依赖反派、阴谋、复仇或突发奇迹。
      decision_ref: PAD-SEL-001
    - path_id: PATH-002
      status: rejected
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 以社区家常菜活动为轻群像背景，两人一边接受邻里提供的零碎味觉线索，一边重新理解彼此；外部活动只作时间框架，关系仍是核心。
      rejection_reason: 群像容易分散双人关系焦点，并可能让外部活动替人物完成和解。
      decision_ref: PAD-REJ-002
    - path_id: PATH-003
      status: rejected
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 用交替回忆与当下试菜形成双时间线，逐步揭示二人失和与菜谱失传的关系。
      rejection_reason: 揭秘结构容易误导为阴谋或反转驱动，也会削弱轻盈日常与线性慢燃感。
      decision_ref: PAD-REJ-003
    - path_id: PATH-004
      status: rejected
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 两人各自坚持一套复原方案，通过带竞技感的连续试做分出高下，最后发现两种做法需要合并。
      rejection_reason: 胜负框架偏向爽感和套路式和解，不如共同劳动自然，也可能把友谊降格为技术输赢。
      decision_ref: PAD-REJ-004

character_engines:
  - character_id: CHAR-001
    role: 退休厨师甲
    want: 复原记忆中的家常味，也证明自己仍有用、仍记得准确。
    fear: 承认记忆有误等于承认衰老，并再次暴露自己对旧友的在意。
    agency: 主动提出或接受共同试做，在关键处选择让步、道歉与继续合作。
    cost: 放下职业自尊，承认当年自己伤人且个人记忆并不完整。
    change: 从把正确等同于尊严，转为接受味道与友谊都需要共同补全。
  - character_id: CHAR-002
    role: 退休厨师乙
    want: 找回那道菜，也确认昔日友谊不是只有自己珍惜。
    fear: 再次合作会重演被轻视、被支配或被抛下的经历。
    agency: 设定合作边界，提供关键感官记忆，并在可以离开时主动留下完成最后一次试做。
    cost: 放弃用冷淡保护自己，明确说出旧伤与仍然在意的事实。
    change: 从以疏离维持体面，转为允许一段不完美的友谊重新开始。
  shared_engine:
    desire: 复原菜味。
    deeper_need: 重新确认彼此在对方生命中的位置。
    conflict_source: 厨艺习惯、记忆偏差、旧日自尊和未说开的伤害。
    resolution_method: 共同劳动、边界协商、主动表达与互相承担；不靠第三方救场或偶然真相。

structure:
  form: linear_dual_protagonist
  units:
    - ordinal: 1
      function: 因失传家常菜重新碰面，建立合作的现实理由与尴尬距离。
      state_change: 从完全疏远变为有限合作。
    - ordinal: 2
      function: 分头寻找材料与回忆，各自版本互相冲突，日常嘴仗产生喜剧。
      state_change: 从礼貌回避变为敢于争执。
    - ordinal: 3
      function: 数次试做各有接近也各有失败，旧伤通过具体动作和用词逐渐浮出。
      state_change: 从争做“正确的人”变为看见对方的付出。
    - ordinal: 4
      function: 一次看似最接近的成品仍不对，两人面临终止合作的选择。
      state_change: 从依赖菜谱目标变为主动选择彼此。
    - ordinal: 5
      function: 两人用各自不完整的记忆共同完成新版本，并承认它不是原样复制。
      state_change: 从修复一道菜转为重启一段平等友谊。

narrative_voice:
  language: zh-CN
  perspective: 近距离第三人称，双主角重心平衡，可按场景有限切换但不在段内跳视角。
  tone: 克制、温暖、带生活观察的轻喜剧。
  humor_sources: 职业习惯的碰撞、嘴硬与行动反差、退休生活细节、试菜中的小失误。
  emotional_method: 少做煽情宣告，以递工具、留饭、改口、等人等动作承载关系变化。
  forbidden_drift: 不转锋利黑色、不制造恶意反派、不靠羞辱老人取笑、不把衰老写成单一笑料。

slow_burn_pacing:
  mode: slow_burn
  progression_rule: 每个单元至少改变关系、认知、选择或合作方式之一，但不一次完成和解。
  escalation: 从客套合作到技术争执，再到旧伤显影，最后才出现明确情感承认。
  breathing_space: 保留买菜、备料、等火、尝味和收拾厨房等日常停顿，让沉默产生意义。
  comedy_density: 轻而持续，不用密集包袱破坏情绪余韵。
  anti_stall_rule: 慢不等于空转；连续场景不得重复同一种争执且毫无状态变化。

payoff_type:
  primary: relational_reconciliation
  secondary: collaborative_creation
  culinary_payoff: 最终菜品可以不是失传原味的完美复制，而是两人共同完成、愿意再次分享的新版本。
  emotional_payoff: 两人以可见行动和一句克制但明确的话确认重新成为朋友。
  promise_preserved: 回报来自关系修复与共同创造，不来自压倒对手、复仇成功、阴谋揭露或黑暗反转。

six_gate_preflight:
  overall_status: ready_for_internal_draft_not_executed
  note: 当前仅做写前预检，无正文，门禁不得虚称已通过。
  gates:
    - gate_result_id: GATE-PREFLIGHT-001
      gate: story_facts
      status: ready_not_run
      check: 五项客户事实已锁定；后续新增时间、地点、菜名与失和原因必须登记来源且互不矛盾。
    - gate_result_id: GATE-PREFLIGHT-002
      gate: character_agency
      status: ready_not_run
      check: 双主角均具欲望、恐惧、选择、代价与变化；和解必须由两人主动促成。
    - gate_result_id: GATE-PREFLIGHT-003
      gate: causality
      status: ready_not_run
      check: 每次试做结果必须推动下一次选择；旧伤揭示需由当下言行触发，不靠无铺垫揭秘或巧合解局。
    - gate_result_id: GATE-PREFLIGHT-004
      gate: pacing
      status: ready_not_run
      check: 慢燃分级明确，每个结构单元必须产生状态变化，禁止连续空转。
    - gate_result_id: GATE-PREFLIGHT-005
      gate: sustainability
      status: ready_not_run
      check: 进展依靠新选择与新后果，不重复同一争执；故事在关系重启处完成承诺。
    - gate_result_id: GATE-PREFLIGHT-006
      gate: plot_continuity
      status: ready_not_run
      check: 线性五单元具有承接；材料、信息、目标和关系变化都须有可追踪来源。

exposure_accounting:
  novel_body_count: 0
  external_exposure_count: 0
  midprocess_intervention_count: 0
  shorthand: 正文0/外露0/中途0
```
