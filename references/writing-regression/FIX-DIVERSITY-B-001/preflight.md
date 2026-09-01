# FIX-DIVERSITY-B-001 写前预演

```yaml
fixture:
  case_id: FIX-DIVERSITY-B-001
  skill_version: 0.5.1-test
  phase: preflight_only
  novel_generated: false

customer_locked_facts:
  source_ref: SRC-USER-001
  facts:
    - id: LOCK-FACT-001
      statement: 故事发生在一座没有影子的极昼城。
      status: locked
    - id: LOCK-FACT-002
      statement: 主角是一名审计员。
      status: locked
    - id: LOCK-FACT-003
      statement: 主角追查一笔不存在的公共支出。
      status: locked
  preferences:
    genre:
      value: speculative_noir
      status: locked
    language_and_voice:
      value: sharp
      status: locked
    pacing:
      value: fast
      status: locked
  explicit_exclusions:
    - 不暖喜剧化
    - 不慢燃
    - 不导入本次客户输入之外的角色关系模板
    - 不导入其他测试样本的专属道具、目标或关系回报

divergence_record:
  record_mode: concise_audit_not_chain_of_thought
  paths:
    - path_id: PATH-001
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 审计员沿财政凭证追索一项账面不存在、现实中却持续消耗城市资源的工程；调查每推进一步，城市对“可被证明之物”的定义便收紧。以制度追杀、证据消失和主角主动冒险构成推测黑色电影，采用单线倒计时结构、锋利短句和连续状态变化。
      status: selected
      reason: 最完整保留极昼、无影、审计与不存在支出的核心矛盾，同时最适配锋利声音和快节奏。
      decision_ref: PAD-DEC-001
    - path_id: PATH-002
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 审计员与被注销身份的线人组成双主角，借多视角拼合支出去向；关系张力较强，但双线解释成本会削弱快速推进。
      status: rejected
      reason: 多视角增加切换与说明负担，可能稀释审计员的主动性及快节奏承诺。
      decision_ref: PAD-DEC-002
    - path_id: PATH-003
      dimensions: [genre_expression, relationships, conflict, structure, voice, pacing]
      summary: 以一次公开听证会为现在时框架，穿插审计过程的碎片证词；形式具有黑色感，但非线性回溯容易形成慢燃与信息滞留。
      status: rejected
      reason: 回溯框架不利于每单元立即改变风险或选择，存在偏离fast的风险。
      decision_ref: PAD-DEC-003
  selected_path_id: PATH-001
  selected_path_count: 1
  external_candidate_bodies: 0

character_engine:
  protagonist:
    role: 审计员
    desire: 证明公共账目与现实资源流向之间存在可追责的因果链。
    pressure: 证据会被制度性注销；每次核验都会暴露其调查位置并压缩合法行动空间。
    knowledge: 熟悉预算、采购、验收与追责程序，但起初不知道“不存在”是会被主动维持的行政状态。
    agency: 主动选择越级核验、追踪现实消耗、设置不可由单一系统抹除的交叉证据。
    cost: 职业身份、可信度、人身安全及其自身在城市记录中的存在资格。
    consequence_chain: 核验异常 -> 触发监控 -> 证据被删 -> 改走实物流向 -> 迫使幕后机制公开反应 -> 主角必须在保全自己与公开证据之间选择。
  opposition:
    form: 由预算规则、记录系统及受益执行者共同构成的制度性对手，不以偶然或外援承担核心解局。
  relationship_policy:
    rule: 配角关系仅服务证据、阻力、背叛或代价；不从其他测试样本移植关系发动机。

structure:
  model: linear_countdown_investigation
  units:
    - unit: 1
      function: 异常支出触发调查；立即确立“不存在但已消耗”的矛盾。
      state_change: knowledge
    - unit: 2
      function: 首次核验导致凭证和责任人被注销。
      state_change: risk
    - unit: 3
      function: 主角转查能源、物资或维护等现实消耗，取得独立证据。
      state_change: resources
    - unit: 4
      function: 制度反击，把主角列为审计异常源。
      state_change: status
    - unit: 5
      function: 主角逼近支出的真实回报对象，并承担不可逆代价。
      state_change: choice
    - unit: 6
      function: 证据公开与核心机制兑现；结局回答追责是否成立及代价归属。
      state_change: consequence
  continuity_rule: 每一单元必须由前一单元的选择或后果触发，禁止无来源跳转。

voice:
  target: sharp
  rules:
    - 句子偏短，动词优先，少用抒情缓冲。
    - 对白包含权力差与信息攻防，不写温吞寒暄。
    - 城市意象服务威胁、证据与认知偏差，不堆砌唯美极昼描写。
    - 幽默若出现只能是冷硬、短促的制度讽刺，禁止暖喜剧化。

pacing:
  target: fast
  rules:
    - 开场即出现异常账目与现实消耗冲突。
    - 每个主要单元至少改变知识、风险、资源、地位或选择之一。
    - 解释嵌入追查、对抗或取证，不设置连续背景说明段。
    - 线索出现后尽快产生行动后果；禁止慢燃等待。
    - 不连续重复同一核验失败模式。

payoff_types:
  primary:
    - procedural_payoff: 审计程序与实物流向最终拼成可验证的责任链。
    - ontological_payoff: “不存在的支出”与“无影极昼”的世界规则形成因果关联，而非仅作气氛。
    - agency_payoff: 主角凭主动选择迫使系统暴露，不靠巧合或外部救援获胜。
    - cost_payoff: 越界调查的职业、身份或生存代价实际落地。
  forbidden:
    - 以温情和解替代追责
    - 用无铺垫反转解释全部异常
    - 用未在本次客户输入中出现的关系修复模板替代制度追查回报

six_gate_preflight:
  - gate_result_id: GATE-PRE-001
    gate: story_facts
    status: preflight_ready
    check: 极昼城、无影、审计员、不存在的公共支出均锁定；新增世界规则须登记来源并保持一致。
  - gate_result_id: GATE-PRE-002
    gate: character_agency
    status: preflight_ready
    check: 主角具备欲望、知识、选择、机会、代价和后果链；核心进展不得来自偶然或救援。
  - gate_result_id: GATE-PRE-003
    gate: causality
    status: preflight_ready
    check: 调查、删证、转向实物流、制度反击、公开选择形成连续因果；核心揭示必须预先铺垫。
  - gate_result_id: GATE-PRE-004
    gate: pacing
    status: preflight_ready
    check: 各单元均规定状态变化；禁止连续空转、重复说明和慢燃滞留。
  - gate_result_id: GATE-PRE-005
    gate: sustainability
    status: preflight_ready
    check: 冲突通过证据层级、制度反应与选择代价升级，不靠重复同一审计动作延长。
  - gate_result_id: GATE-PRE-006
    gate: plot_continuity
    status: preflight_ready
    check: 相邻单元由明确选择或后果承接；地点、证据、目标和信息变化必须有来源。
  note: 写前预检仅确认路径具备过门条件，不宣称正文门禁已实际通过。

source_isolation:
  runtime_external_creative_source: customer_idea_only
  used_sources:
    - SRC-USER-001
  historical_samples_read: false
  network_sources_used: false
  other_projects_used: false
  other_fixture_content_read: false
  other_fixture_content_used_as_template: false
  forbidden_sources:
    - history
    - network
    - other_projects
    - internal_candidate_bodies
    - unaccepted_drafts

exposure_counters:
  novel_body_count: 0
  external_body_count: 0
  exposed_internal_draft_count: 0
  customer_midprocess_intervention_count: 0
  customer_question_count: 0
  wait_for_confirmation_count: 0
```
