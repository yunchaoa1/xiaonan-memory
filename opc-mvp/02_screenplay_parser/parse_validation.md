# 解析验证

## 结论

**PASS（带已记录适配）**：`sample.fountain` 已由真实的 `screenplay-tools` Python 包 0.0.10 解析，不是手工伪造解析结果。最终原生结果为 12 个元素；归一化后为 22 个节点、1 个完整场景。

## 环境与安装

- 主机：Windows 11；命令由 Git Bash/MSYS 执行。
- Python：3.11.15。
- 包：PyPI `screenplay-tools==0.0.10`，wheel 约 20 KB；使用 `--no-deps --target` 安装到 `%LOCALAPPDATA%/Temp/screenplay-tools-runtime`，未安装大型无关依赖，未写入项目环境。
- npm 探测：`npm view screenplay-tools` 返回 E404；该项目可用分发在 PyPI，故采用 Python 实现。

实际安装命令成功：

```bash
python -m pip download --no-deps screenplay-tools -d "$LOCALAPPDATA/Temp/screenplay-tools-download"
python -m pip install --no-deps --target "$LOCALAPPDATA/Temp/screenplay-tools-runtime" screenplay-tools==0.0.10
```

## 最终解析命令

```bash
PYTHONPATH="$LOCALAPPDATA/Temp/screenplay-tools-runtime" python - <<'PY'
from pathlib import Path
from screenplay_tools.fountain.parser import Parser
p = Path(r'D:/Hermes/xiaonan-memory/opc-mvp/02_screenplay_parser/sample.fountain')
fp = Parser()
fp.add_text(p.read_text(encoding='utf-8'))
fp.finalize()
print(fp.script.dump())
print('COUNT', len(fp.script.elements))
PY
```

真实输出中的关键行：

```text
HEADING:"S02 外景 · 村口老槐树下 · 日（连续）" (S02)
ACTION:"王二像忽然想起什么，伸手探进牛满怀里。"
CHARACTER:"王二"
DIALOGUE:"老爷还说，贱骨头身上说不定藏着私货。搜一搜。"
...
PARENTHETICAL:"大笑"
DIALOGUE:"赎身？一个克夫的扫把星，还想赎身？做梦去吧你！明儿到了窑子里，多的是客人给你赏钱！"
COUNT 12
```

原生元素计数：

| 类型 | 数量 |
|---|---:|
| HEADING | 1 |
| ACTION | 4 |
| CHARACTER | 3 |
| PARENTHETICAL | 1 |
| DIALOGUE | 3 |
| 合计 | 12 |

归一化 AST 计数（实际生成结果）：

```json
{"scene_count":1,"normalized_node_count":22,"types":{"action":12,"character":3,"dialogue":3,"parenthetical":1,"scene_heading":1,"sound":2}}
```

## 发现的兼容问题与适配策略

1. **中文强制场景标题陷阱**：直写 `.外景. ...` 在 0.0.10 中未识别。源码 `_parse_forced_scene_heading()` 使用 `^\.[a-zA-Z0-9]`，要求点号后第一个字符是 ASCII 字母或数字。最终采用 `.S02 外景 · ... #S02#`；`S02` 是兼容前缀，中文仍保留在标题正文。
2. **中文角色名**：普通角色规则面向大写拉丁字符；统一使用 `@王二`，真实解析为 `CHARACTER`。
3. **中文全角括号不是插入语**：解析器匹配 `^\(.*\)$`；将源稿 `（大笑）` 转成 `(大笑)`，AST 内容仍为中文“ 大笑 ”（无括号）。
4. **动作合并**：默认 `mergeActions=True`，多个 `!` 动作即使以空行分隔也可能合并为一个 ACTION，文本内部保留双换行。适配层按 `\n\n` 拆为独立 `action` 节点，以恢复段落粒度。
5. **音效无原生专类**：`【音效】咔。` 以强制 ACTION 解析；适配层识别前缀并映射为 `sound`，同时记录 `source_element_type: ACTION`，保证可追溯。
6. **强制角色的 `forced` 标志缺失**：0.0.10 的 `_parse_forced_character()` 创建 `Character` 时没有传 `forced=True`；因此标准 AST 不依赖此布尔值判断角色来源，只依赖输入约定和类型结果。
7. **AST 生成方式**：直接读取 `fp.script.titleEntries` 与 `fp.script.elements` 的对象字段，按顺序生成节点；不解析面向人看的 `dump()` 字符串。

## 内容核验

- 样本对应源文件第 29—67 行，包含场景标题、动作、三段王二对白、插入语、两处音效及结尾情绪结果，构成完整场二。
- 未改写对白含义与事件顺序；仅作 Fountain 标记和半角括号适配。
- `normalized_screenplay.json` 明示源文件、源行范围、解析器版本、原生计数和归一化规则。
- JSON 已由 Python `json.dumps` 生成，可被标准 JSON 解析器读取。

## 阻断状态

无阻断。npm 包名不可用，但 PyPI 官方同名分发可下载并成功执行；因此已完成真实解析验证。
