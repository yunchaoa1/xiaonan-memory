# 02_screenplay_parser

OPC MVP 的最小剧本解析样本：从已验收的《十二时辰》第一章 v0.3 中截取**场二（第 29—67 行）**，转为 UTF-8、Fountain 1.1 兼容的中文强制标记文本，再以 `screenplay-tools` 0.0.10 实际解析并归一化为 AST JSON。

## 文件

- `sample.fountain`：小而完整的单场景 Fountain 样本。
- `normalized_screenplay.json`：解析结果经 OPC 适配层归一化后的 AST。
- `parse_validation.md`：真实运行环境、命令、输出、缺陷与适配策略。

## 中文强制标记约定

Fountain 的自动识别偏英语，本样本不把中文标题/角色名交给启发式判断：

- `.S02 外景 · 村口老槐树下 · 日（连续） #S02#`：`.` 强制场景标题；`S02` 紧跟点号是为兼容当前解析器的 `^\.[a-zA-Z0-9]` 实现；末尾 `#S02#` 是场号。
- `!动作`：`!` 强制动作。
- `@王二`：`@` 强制中文角色提示。
- `(大笑)`：Fountain 半角括号强制/识别插入语；不使用中文全角括号。
- `【音效】`：先作为强制动作进入解析器，再由 OPC 适配层归一化为 `sound` 节点。

## 最小复现

系统未全局安装 `screenplay-tools`；验证使用隔离目标目录，未修改项目依赖：

```bash
python -m pip install --no-deps --target "$LOCALAPPDATA/Temp/screenplay-tools-runtime" screenplay-tools==0.0.10
PYTHONPATH="$LOCALAPPDATA/Temp/screenplay-tools-runtime" python parse_or_dump.py
```

本目录未保留一次性验证脚本；实际解析命令与输出摘要完整记录在 `parse_validation.md`。生产节点应把相同映射固化为版本化适配器，而不是直接依赖 `dump()` 文本。

## AST 边界

`normalized_screenplay.json` 是 OPC 自定义标准化结构，不声称是 `screenplay-tools` 原生 JSON。原解析器合并相邻动作，因此适配层按空行拆回动作段，并将 `【音效】` 提升为 `sound`。剧情事实、台词和顺序均保持源稿，不新增镜头或资产事实。
