---
name: h3-segment-filmmaking
description: 做 H3 多段成片时加载：分段算时长、定图槽、机检。
version: 1.0.2
author: 小南
license: MIT
metadata:
  hermes:
    category: creative
    tags: [h3, multi-segment, filmmaking, lint, qc]
---

# H3 多段成片 · 分段与机检

一份台词剧本 → N 段 H3 素材 → 拼成一条成片。

**这是 `forest-laoli-h3`（H3 专用全流程技能，写提示词的规矩都在那）的施工手册。两个一起用：那边管"怎么写对"，这边管"怎么算、怎么拆、怎么查、怎么拼"。**

---

## When to Use（什么时候加载）

凡哥说「把这段做成视频」「跑一版成片」「把剧本拍出来」「一集一集出」「上次那个重做」时加载。

⛔ **先跑 `python D:\Hermes\scripts\find_skill.py h3`，把命中技能的描述第一句读完再动手。** 按技能名字猜用途会挑错（`sd-storyboard-engine` 看着像分镜，`forest-laoli-h3` 看着像人格壳，实际正相反）。

---

## 第 0 步 · 先找上次跑通的原件，不许重新发明

**任何"上次做过"的活，开工前先找这三样：**

| 找什么 | 去哪找 |
|---|---|
| 上次的提交脚本 | `D:\Hermes\cache\submit_*.py`（按修改时间排序，找成片生成时间之前那一版） |
| 上次的提示词原文 | `D:\Hermes\cache\seg0*.txt`，或 `D:\Documents\我的文档\07_影剧工坊跑通\<剧名>\04_分镜节点*.md` |
| 上次的载荷构造器 | `D:\Hermes\cache\build_payload.py`、`wf2api.py` |

```bash
ls -lat /d/SDkecheng/ComfyUI/output/*.mp4 | head        # 成片什么时候出的
find /d/Hermes/cache -maxdepth 1 -name "*.py" -newermt "<成片前一天>" ! -newermt "<成片当天+1>"
```

**照抄，只改内容不改结构。** 重新发明一遍的代价是几小时素材全部作废。

---

## 第 1 步 · 算段表（先算后写，不许拍脑袋）

### 1.1 三个硬数字

| 量 | 值 | 出处 |
|---|---|---|
| 中文口播语速 | **3.3 字/秒**（含标点停顿） | `D:\Hermes\skills\creative\forest-laoli-h3\references\` 里的 dialogue-density（实测标定） |
| 台词填充率 | **80–90%**（低于 65% 观众觉得"怎么没人说话"；高于 95% 盖掉动作和呼吸） | 同上 |
| 句数密度 | 强爽 **20–24 句/分钟**；**低于 12 句/分钟必崩** | 同上 |
| 单段上限 | **15 秒**（15.08 被 ComfyUI 直接拒，14.38 正常出片） | H3 实测 |

### 1.2 算法

```
该段台词字数 ÷ 3.3 = 台词占用的秒数
段时长 = 台词秒数 ÷ 0.85
段时长 > 15 秒 → 必须拆段，不许硬塞
每段句数 = 段时长 × 3.3 ÷ 11字（平均句长）≈ 4 句
```

**示例（49 句 / 562 字）**：562 ÷ 3.3 = 170 秒纯台词，÷ 0.85 = **200 秒**，÷ 平均 10 秒/段 ≈ **20 段**。

### 1.3 两条结构铁律

1. **一段一个空间。** 咨询室说到一半切老家，那是两个空间 → **必须拆两段**。模型会把两个空间画进同一段。
2. **闪回单独成段。** 现在时的对话里她说"我小时候……"，画面切童年 → 现在时一段、闪回一段，不许混。

### 1.4 长句拆开，内容不许动

- 单次开口 **≤15 字**，超 20 字必拆。
- 拆完 **必须跑覆盖核对**（见第 4 步）。历史上「拆句后忘了补镜」，静默丢了 11 句台词，人眼查不出来。

---

## 第 2 步 · 定图槽（一次钉死，每段全挂）

**全片固定 N 张图（上限 9），顺序一次钉死，每段都挂全部，一张都不许省。**

省掉中间一张 → 后面所有 `<Picture N>` 全部错位 → 咨询室戏喂进妈的图。

**典型 9 槽（人物→场景→道具）：**

| 槽 | 内容 | 例 |
|---|---|---|
| 1–4 | 出场人物四视图 | 她 / 他 / 妈 / 小女孩 |
| 5–7 | 主要场景（平视主视角） | 咨询室 / 老家餐厅 / 老家门口 |
| 8–9 | 关键道具（一件一张，禁宫格） | 新书包 / 旧书包 |

**写法**：每段 `subject_definitions` 里只定义本段用到的 Subject，但 `<Picture N>` 的编号必须与全局槽位一致：

```
<Subject 1> is the woman, defined by <Picture 1>. Follow ...   ← 槽 1 = 她
<Subject 5> is the therapy room, defined by <Picture 5>. ...   ← 槽 5 = 咨询室
```

**排完后必查**：

```bash
grep -h -o "Picture [0-9]" seg*.txt | sort | uniq -c | sort -k2   # 编号分布
grep -o "<Subject [0-9]> is" seg01.txt                            # 每段定义了几个
```

---

## 第 3 步 · 写提示词（规矩在 forest-laoli-h3 / h3-video-prompt）

只记这一条就够开工，其余照 `forest-laoli-h3` 六阶段走：

> **⛔ 台词必须写进正文 `<d>[Chinese] 台词</d>`，绝不许抽成 mp3 去做后期配音。**
>
> 抽出去 = H3 没台词可念 = 自己编 = 编出**英文** = 口型跟着英文走 = 后期中文对不上 = 全片作废。

`build_payload.py` 的 `build()` **返回的是文件路径，不是 dict**，要 `json.load` 读回来再提交，否则 ComfyUI 报 `'str' object has no attribute 'items'`。

---

## 第 4 步 · 机检（不跑等于没写）

### 4.1 逐段跑 `h3_lint.py`，必须 FAIL 0

```bash
cd /d/Hermes/skills/creative/forest-laoli-h3
python scripts/h3_lint.py "D:/Hermes/cache/emotion/seg01.txt" --duration 14 --aspect 9:16
```

批量版：`scripts/lint_all_segs.py`（本技能自带，改一下段表一次跑完）。

### 4.2 台词覆盖核对

```bash
python scripts/check_dialogue_coverage.py <台词原稿.md> <seg目录>
```

**三条验收**：原稿句数全部覆盖 / 每段 `<d>` 数 ≈ 该段镜数（留白段可 −1）/ 无凭空多出来的句子。

⚠️ **两类误报已修（2026-11-22 实测《偏心》撞到，v1.0.2）**：
1. 台词稿里以 `>` 或 `#` 开头的说明行/标题行会被当台词抽出来（规则里常拿「她说」「我告诉她」举例）→ 现已跳过这两类行；
2. 省略号写法不一致（`...` 与 `…`）导致比对失败 → 标点集已补 `.．-`。

报「缺 N 句」时先 `grep` 这两句话在不在 seg 里，再判真缺还是脚本假报。

### 4.3 常见 FAIL 与改法（全部是实测撞过的）

| 机检项 | 症状 | 改法 |
|---|---|---|
| **H13** | 命中 `not` / `without` / `never` | **否定会被直接画出来**。改成正面陈述：`does not change`→`stays the same`；`cries without sound`→`cries silently`；`does not move anything else`→`keeps everything else still` |
| **H13** | 软词 `slightly` / `very` / `line` / `frame` | 换成可见事实：`slightly above her eye line`→`a little above her eyes` |
| **H13** | 镜行缺分号分区 | 格式必须是 `[Shot N] 景别·机位·运镜; 正文动作和台词` |
| **H2** | 切点时间 ≥ 段时长 | `--duration` 传错，或段被改短了没改时间戳 |
| **H9** | 画外声缺固定短语 | 必须逐字写 `says in an off-screen voiceover`，中间不许插词 |
| **H22** | 道具首现没写支撑 | 写清在哪：`the bowl sits on the near edge of the table` / `in her hands`，否则悬浮 |
| **H23** | 单镜 >75 词 | 压到 ≤70，超了会丢机位 |
| **H24** | 缺维持句 | 补 `the two armchairs stay at the two ends of the table`，否则站位家具漂移 |
| **H27** | 末镜无定格句 | 最后加 `The movement stops and the picture holds still for the last second.` |
| **H29** | 人穿过门洞/门框 | **会变半透明融化**。改成走到门口停住：`walks to the far doorway and stops at the threshold` |
| **H30** | 同镜引用同一 Subject 多次 | 一镜最多两人，第二人别写旁观动词 |

**可豁免的 WARN**：H5（场景标签定义了但正文没引用，正常）、H18（对话段连续静止镜，正常）。

**H20 填充率不足不一定是错**：在 summary 里标 `this segment plays as a held-breath beat` 就成立，但低于 40% 是真的没人说话，要缩短段长。

---

## 第 5 步 · 提交与合成

- 提交：`{"prompt": payload}`，`mode` 必须显式 `ref2va`，竖屏 `w=544 h=960`，成片统一放大到 810×1440。
- 参考图缩到 1024 宽；5 张 2848×1600 一起 VAE 编码会 `Fatal Python error: Aborted`。
- 12–14 秒一段，RTX 5080 Laptop 16GB 约 **10–15 分钟/段**（首段含 32B 文本编码器加载，更慢）。
- **队列会丢**：ComfyUI 重启后 pending 全没，跑前先 `curl -s http://127.0.0.1:18188/queue` 确认，别以为提交了就一定在跑。
- 合成：段按序 concat → 按段内切点对齐 → 字幕分三层（她/他/关键句）→ 混音。

---

## 出片必做的验收（别只看出没出片）

1. **ASR 回读**：抽音频转写，确认说的是中文、句数和稿子对得上。英文就是台词没写进提示词。
2. **抽帧看关系**：两个人凑太近、像恋人 = 没定距离。每场写死"隔茶几、间距一米六、不接触"。
3. **抽帧看景别**：写"中景"画成怼脸特写 = 参考图占了构图，压景别描述。

```bash
"/d/tools/ffmpeg/ffmpeg" -y -i 成片.mp4 -vn -ac 1 -ar 16000 out.wav
# 转写模型在 D:/Hermes/models/faster-whisper-large-v3（不要从 HF 下，连不上）
```

⚠️ ffmpeg 不认 `/d/` 前缀路径，一律写 `D:/...`。

---

## 支持文件

| 文件 | 用途 |
|---|---|
| `scripts/lint_all_segs.py` | 按段表批量跑 h3_lint，汇总 FAIL/WARN |
| `scripts/check_dialogue_coverage.py` | 台词原稿 vs `<d>` 块覆盖核对，揪出拆句丢句 |
| `references/lint-pitfalls.md` | 机检常见项的完整对照（含原文与改后写法） |
| `references/case-2026-12-19-pianxin.md` | 《偏心》全废与重做实录：三小时素材作废的完整因果 |

---

## 主控台登记

改本技能后同步 `DASHBOARD.md` 与 `skill-router` 路由表。
