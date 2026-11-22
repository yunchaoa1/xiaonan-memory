# h3_lint.py 机检对照表（实测撞过的项）

机检真身：`D:/Hermes/skills/creative/forest-laoli-h3/scripts/h3_lint.py`
共 30 项，只查**字面**能查的东西。人眼看不出来的，它全查得出来。

```bash
cd /d/Hermes/skills/creative/forest-laoli-h3
python scripts/h3_lint.py "D:/Hermes/cache/emotion/seg01.txt" --duration 14 --aspect 9:16
```

`--duration` 必须与真实段长一致，否则 H2 会误报切点越界。

---

## FAIL（必须清零）

### H13 · 否定词根会被直接画出来

**原理**：模型不理解"不"，只理解名词和动词。写 `not change` 它就画"变化"，写 `without sound` 它就画"声音"。

| 原文（FAIL） | 改后（OK） |
|---|---|
| `the light on the table does not change` | `the light on the table stays the same` |
| `her hands working without looking up` | `her hands working, her eyes on the bowls` |
| `his eyes not moving off her` | `his eyes fixed on her face` |
| `he does not move anything else` | `he keeps everything else still` |
| `cries without sound` | `cries silently` |
| `her next words not arriving` | `her mouth staying open, the breath going out of her` |
| `She never steps through the doorway` | `She stays in the hallway` |
| `He tells her not to` | `He tells her to stop apologising` |

**硬词根**（一票否决）：`not` / `no` / `never` / `without` / `nothing` / `none`
**软词根**（WARN，建议换）：`slightly` / `very` / `line` / `frame` / `somewhat`

### H2 · 切点时间超过段时长

症状：`[Shot 4] 切点 9.00s ≥ 段时长 8.0s`

成因两种：① `--duration` 传错（段实际 12 秒，检查时传了 8）② 段被压缩了但时间戳没跟着改。

### H9 · 画外声缺官方固定短语

必须是逐字：`says in an off-screen voiceover`
写成 `says in a low flat off-screen voiceover at a slow pace` **不合格**——中间插了词。

正确：`says in an off-screen voiceover, low and flat, at a slow pace`

### H13 · 镜行缺分号分区

格式必须是：

```
[Shot N] 景别·机位·运镜; 正文（主体 + 可见动作 + 台词 + 维持句）
```

分号前是"怎么拍"，分号后是"拍到什么"。用句号代替分号 = 分区失败。

---

## WARN（要判断，不一定改）

### H22 · 道具首现没写支撑 → 悬浮

```
✗ the blurred bowl sits in the near foreground
✓ the blurred bowl sits on the near edge of the table
✓ stacks the bowls one on another in her hands
```

只要写清"在哪/在谁手上"就过。H3 无法推断物件的支撑关系。

### H23 · 单镜 >75 词 → 丢机位

压到 ≤70。删的顺序：次要氛围描写 → 重复的空间补述 → 形容副词。

### H24 · 缺维持句 → 站位和家具会漂

关键镜（有人的、有机位变化的）补一句：

```
the two armchairs stay at the two ends of the table
```

### H27 · 末镜无定格句

最后一句加：

```
The movement stops and the picture holds still for the last second.
```

### H29 · 消除式动作（人穿过门洞/门框）

**症状**：人走进门框会变半透明融化（H3 的合成缺陷）。

```
✗ walks out through the far doorway
✓ walks to the far doorway and stops at the threshold
✓ the door leaf swings shut, the frame empty
```

要么人在门口停住，要么只拍门动、人不穿框线。

### H30 · 同镜引用同一 Subject 多次

一镜最多两个人。第二人只写存在，不写旁观动词（`watching` / `noticing` 会诱发第二个动作源）。

### H20 · 台词填充率

| 区间 | 判断 |
|---|---|
| 80–90% | 最佳 |
| 65–80% | 可接受，但偏慢 |
| 40–65% | 留白段可以（summary 里标 `this segment plays as a held-breath beat`） |
| < 40% | 真的没人说话，缩短段长或并段 |

### H5 · 定义了却没被引用

场景标签（`<Subject 5>` 咨询室）在正文里不引用是**正常的**——它只是锁外形和空间。可豁免。

### H18 · 连续 ≥3 镜全静止

对话段（正反打、特写对峙）是**正常的**。可豁免。
但如果是**单镜**静帧超过 2.5 秒，必须给位移（4–6cm 微推）或加台词，否则观众看出是定格。

---

## 检查项速查（按字母）

| 项 | 查什么 |
|---|---|
| H1 | 六段式字段齐全、顺序正确 |
| H2 | 第 1 镜无时间戳；后续切点 < 段时长 |
| H3 | 段时长合规（≤15s） |
| H4 | 正文无中文残留（`<d>` 外） |
| H5 | 标签定义 vs 正文引用 |
| H6 | retention 标记合法 |
| H9 | 画外声固定短语 |
| H10 | `overall_soundscape` 不许出现音乐词（BGM 只放 `non_diegetic_music`） |
| H12 | `[Shot 1]` 必须有具名主体（空镜开场易被划走） |
| H13 | 镜行分区 + 词根干净 |
| H14 | 画幅声明（`--aspect 9:16`，禁 auto，全片一致） |
| H16–H19 | 禁用运镜 / 运镜与景别匹配 / 运镜有变化 / 位移不叠变焦 |
| H20 | 台词填充率与句数密度 |
| H21 | 相邻两镜同一说话人连续开口（站桩） |
| H22 | 道具支撑 |
| H23 | 单镜词数 ≤70 |
| H24 | 维持句 |
| H25 | 单镜 60–90 词区间 |
| H27 | 末镜定格句 |
| H28 | 空间描述无复数扩建词（`several chairs` 会画一堆） |
| H29 | 消除式动作 |
| H30 | 同框人数 |
| H31 | 门窗开闭与画外声源隔离 |
| H32 | 段内角色位置依托物前后一致 |
| H33 | 高危卡死/冻帧物理动作 |
| H35 | 氛围层齐（光位 / 空气介质 / 前景景深） |
