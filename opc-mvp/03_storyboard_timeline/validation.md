# OPC MVP 三镜 OTIO 验证

## 范围

- 仅落地 3 镜，未扩展全 15 镜。
- 来源：`D:/Hermes/xiaonan-memory/opc-mvp/02_screenplay_parser/normalized_screenplay.json`
- 场次：`scene.S02`
- OTIO：OpenTimelineIO `0.18.1`
- 时间基准：24 fps

## 实际命令

```bash
python "D:/Hermes/xiaonan-memory/opc-mvp/03_storyboard_timeline/build_and_validate_otio.py"
```

命令退出码：`0`

## 写入后回读结果

脚本先通过 OTIO API 写入 `timeline.otio`，随后用 `otio.adapters.read_from_file()` 从磁盘回读，并仅对回读对象执行断言。

| 镜头 | 回读时长 | ≤15秒 | shot_id metadata | scene metadata | node数 | status |
|---|---:|---|---|---|---:|---|
| S02-01 | 12.0s | PASS | S02-01 | scene.S02 | 4 | MVP |
| S02-02 | 13.0s | PASS | S02-02 | scene.S02 | 7 | MVP |
| S02-03 | 10.0s | PASS | S02-03 | scene.S02 | 7 | MVP |

- 回读镜头数：`3`
- 回读总时长：`35.0s`
- JSON 声明预期总时长：`35.0s`
- 总时长核对：`PASS`
- 所有镜头 `≤15s`：`PASS`
- timeline metadata：`project=十二时辰 OPC MVP`、`rate=24`、`schema=opc.shots/0.1`、`scope=chapter-1 three-shot timeline smoke test only`、`shot_count=3`、`source_scene_id=scene.S02`
- clip metadata 顺序与 JSON 镜头顺序一致：`PASS`
- 每镜 `opc.status=MVP`：`PASS`
- 综合结果：`PASS`

## 真实标准输出摘要

```json
{
  "otio_version": "0.18.1",
  "readback_timeline": "十二时辰_第一章_OPC_MVP_3镜",
  "total_seconds": 35.0,
  "expected_total_seconds": 35.0,
  "validation": "PASS"
}
```

## 文件

- `opc_shots.json`：三镜结构化数据与预期时间线信息。
- `timeline.otio`：由 OpenTimelineIO API 实际写入的时间线。
- `build_and_validate_otio.py`：可复现的写入、回读与断言脚本。
- `validation.md`：本验证记录。
