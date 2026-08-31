# OPC GPT Image 主体资产节点机器审计规范 v0.1

## 1. 适用范围与封闭边界

本规范用于 OPC GPT Image 下游主体资产节点。审计运行时只允许读取审计清单明确声明的输入；禁止使用聊天补充、临时文件、网络检索、未登记参考图或其他场外输入。

固定上游：
- `D:\Documents\我的文档\十二时辰_第一章_剧本资产提取_Skill测试版v0.11.md`
- `D:\Documents\我的文档\十二时辰_第一章_逐镜资产绑定_v0.11.csv`

## 2. 自动可检项目

1. **必填字段**：`asset_id`、`asset_type`、`spec_version`、`status`、`source_files`、`source_sha256`、`model_id`、`model_config`、`reference_images`、`output_file`、`output_format`、`width`、`height`、`output_sha256`、`qc_status`、`lock_status`、`audit_timestamp`；字段不得为空。
2. **状态枚举**：`status ∈ {DRAFT, GENERATED, QC_PENDING, QC_PASS, QC_FAIL, LOCKED}`；`qc_status ∈ {PENDING, PASS, FAIL}`；`lock_status ∈ {UNLOCKED, LOCKED}`。
3. **ID/版本**：`asset_id` 在本批次唯一且格式稳定；`spec_version` 必须为显式版本号；同一资产迭代不得覆盖旧版本记录。
4. **来源 SHA**：每个上游文件均记录路径与 64 位小写十六进制 SHA-256；文件存在且实算值与声明值一致。
5. **模型 ID 配置**：记录完整 `model_id` 及影响结果的显式配置（至少尺寸、质量/档位、背景/透明度、种子或“不支持/未设置”）；不得依赖未声明默认值。
6. **参考图来源**：每张参考图记录 `ref_id`、路径、SHA-256、来源类型及对应资产；文件必须存在，且不得出现清单外参考图。
7. **输出格式、尺寸、哈希**：输出文件存在；实际格式与 `output_format` 一致；实际宽高与声明值一致；SHA-256 与 `output_sha256` 一致。
8. **QC 与锁定状态**：`QC_PASS` 必须对应 `qc_status=PASS`；`QC_FAIL` 必须对应 `qc_status=FAIL`；`LOCKED` 必须同时满足 `status=LOCKED`、`qc_status=PASS`、`lock_status=LOCKED`。失败或待审资产不得锁定。
9. **禁止场外输入**：审计清单必须声明 `closed_input=true`；实际输入路径及哈希集合必须与清单完全相等，发现未登记输入即失败。

## 3. 必须人工复核项目

机器校验通过后，人工仍须逐资产确认并留下结论与证据定位：

- **身份一致**：人物、动物或主体身份与上游定义及参考图一致，关键辨识特征未漂移。
- **可见事实**：画面中可观察的人数、服饰、姿态、时代特征、环境与上游事实一致。
- **场景拓扑**：空间关系、出入口、前后左右、相邻区域及主体位置不存在自相矛盾。
- **道具结构**：道具类别、部件、连接方式、数量、持握/摆放关系和功能结构合理且符合上游。
- **未知项未被脑补**：上游标为未知、未给出或不可见的信息未被擅自确定；必要时保持中性、遮蔽或明确标注未知。

## 4. PASS / FAIL 规则

- **PASS**：全部自动可检项通过，全部人工复核项均为 `PASS`，无未关闭的严重问题；仅此状态允许锁定。
- **FAIL**：任一必填字段缺失、枚举非法、ID/版本冲突、SHA/路径/格式/尺寸不符、模型或参考图未登记、出现任何场外输入，或任一人工复核项为 `FAIL`。
- **PENDING**：自动检查已通过但人工复核未完成；不得记为 PASS，不得锁定。
- 审计以资产为最小判定单元；批次仅在所有资产均 PASS 时判定 `batch_result=PASS`，否则为 `FAIL` 或 `PENDING`。

## 5. 审计输入格式

UTF-8 JSON；顶层结构：

```json
{
  "audit_spec_version": "0.1",
  "batch_id": "string",
  "closed_input": true,
  "declared_inputs": [{"path": "string", "sha256": "64hex", "role": "upstream|reference"}],
  "assets": [{
    "asset_id": "string",
    "asset_type": "string",
    "spec_version": "string",
    "status": "DRAFT|GENERATED|QC_PENDING|QC_PASS|QC_FAIL|LOCKED",
    "source_files": ["string"],
    "source_sha256": {"path": "64hex"},
    "model_id": "string",
    "model_config": {},
    "reference_images": [{"ref_id": "string", "path": "string", "sha256": "64hex", "source_type": "upstream|approved", "asset_id": "string"}],
    "output_file": "string",
    "output_format": "png|jpeg|webp",
    "width": 0,
    "height": 0,
    "output_sha256": "64hex",
    "qc_status": "PENDING|PASS|FAIL",
    "lock_status": "UNLOCKED|LOCKED",
    "audit_timestamp": "ISO-8601"
  }]
}
```

## 6. 审计输出格式

UTF-8 JSON；机器结果与人工结果分栏，禁止机器代填人工结论：

```json
{
  "audit_spec_version": "0.1",
  "batch_id": "string",
  "batch_result": "PASS|FAIL|PENDING",
  "assets": [{
    "asset_id": "string",
    "machine_result": "PASS|FAIL",
    "machine_checks": [{"check": "string", "result": "PASS|FAIL", "evidence": "string"}],
    "human_result": "PASS|FAIL|PENDING",
    "human_checks": [{"check": "identity|visible_facts|scene_topology|prop_structure|no_invented_unknowns", "result": "PASS|FAIL|PENDING", "reviewer": "string", "evidence": "string"}],
    "final_result": "PASS|FAIL|PENDING",
    "lock_allowed": false,
    "issues": [{"code": "string", "severity": "ERROR|WARNING", "message": "string"}]
  }],
  "audited_at": "ISO-8601"
}
```
