---
name: h3-segment-filmmaking
description: 做 H3 多段成片时加载：分段算时长、定图槽、机检。
version: 1.1.0
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

## 第 -1 步 · 技能读全（2026-11-23 凡哥令 · 比什么都先）

**凡哥原话**：「技能摆在那，头一次你没用，这一次你是用了还用不全？能解决这个问题吗？」

**实测**：`forest-laoli-h3` 有 **54 份文件、20.8 万字**（主文件 + 20 份 references + 33 个 scripts），我只读了 **5 份（25%）**。漏的那批里有个 `checklist.md` —— **62 项检查清单，一条没过**。

**病根**：技能是分层的，我凭「这次需要啥」挑着读。**只要还在挑，就一定漏。** 换成别的技能一样漏 —— 全库体检里 `baoyu-infographic` 45 份参考、`working-with-fange` 27 份、`h3-video-prompt` 13 份，全是「参考多但没机检」。

**规矩：一次读全，不留判断空间。**

```bash
python D:/Hermes/scripts/skill_full.py forest-laoli-h3 --read   # 全部文件一次摊开
python D:/Hermes/scripts/skill_full.py --audit                  # 全库体检，标出高危技能
```

**「参考多但无机检」的技能 = 高危**：没有脚本兜底，只能靠人读全。

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

### 1.2b 两个密度指标打架时，听填充率的（2026-11-22 当场算错过一次）

「20–24 句/分钟」和「80–90% 填充率」**会冲突**：49 句撑出来的片子按填充率算 200 秒 = **16.6 句/分钟**，低于 20 的爽感基准。

**判据**：

| 冲突 | 听谁 |
|---|---|
| 填充率 vs 句数密度 | **填充率优先**。台词一句不许删（凡哥铁律），所以段长只能按字数算；句数密度不够是**这个脚本本身话少**，不是排错了 |
| 句数密度 < 12 句/分钟 | **这才是真崩**，必须处理（要么加台词，要么砍时长） |
| 填充率 < 65% | 要么缩短段长，要么在 summary 标 `held-breath beat` |

**反面教训**：我先按「49 ÷ 20 句/分钟 = 2.45 分钟」排了 2.4 分钟，**算完发现纯台词就要 170 秒，装不下**。正确顺序永远是：**先 ✕ 字数 ÷ 3.3 得到纯台词秒数，再 ÷ 0.85 得到总长**，最后才看句数密度落在哪个区间。

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

## 第 3.5 步 · 表演层：脸要动，调要变（2026-11-23 凡哥打回）

**症状**：镜头、构图、台词全对，凡哥看完只说两件事——**「人的面部表情」**和**「说话的节奏一直不变」**。他明确说「切镜我觉得很棒 很自然」，问题不在镜头。

**《偏心》20 段 200 秒实测**：

| 量 | 实测 |
|---|---|
| 面部四区有动作的段 | **13 段是零**，7 段只有 1–2 区 |
| 她眉毛动了几次 | **0 次**（写着 2 次：一次是 `brown` 颜色词，一次是他） |
| `low flat voice` 出现次数 | **11 次**（6×slow pace + 5×even pace） |
| 台词覆盖时长 | **99%**（200 秒里 196 秒在说话） |
| 句子间隔 <0.3 秒 | **96%** —— 听着像念稿 |

**根因**：`forest-laoli-h3` 的 `references/acting-facs.md`、`acting-recipes.md`、`acting-listen.md` **三份一份没读**。技能主文件第 12 条明写「情绪必须落成眉·眼·口·颌的可见动作，禁写紧张/平静等结论词」，我写的是「表情安静」「手放膝上」。

### 3.5.1 四区：写肌肉，不写结论

| 区 | 写这个 | 禁写 |
|---|---|---|
| 眉 | `her brows pull together` / `the inner ends of her brows lift` / `her brows go flat` | 皱眉、委屈 |
| 眼 | `her lids hang low` / `her eyes stop blinking` / `more white showing` / `the skin under her eyes bunches` | 眼神复杂 |
| 口 | `her lips press into a thin line` / `the corners of her mouth pull down` / `her lower lip pulls inward` | 嘴角扯了一下 |
| 颌 | `her jaw muscles stand out` / `the skin of her chin creases`（忍泪）/ `her jaw goes slack`（愣住） | 咬着牙 |

- **幅度用可见计数**：`her lips part by a finger's width`（不是 slightly open）、`her jaw muscles stand out, two ridges at the sides`（不是 very tight）。
- **「在忍」靠一个不该出现的泄漏动作**：`her throat moves in a swallow` / 手指收紧 / 鼻息加重。
- **注意 `jaw` / `chin` 的统计陷阱**：`jawline`、`chin-length hair` 是外貌描写，机检别把它们算成表情动作。

### 3.5.2 语调必须分段，一段一个调

| 段型 | 语调写法 |
|---|---|
| 平静陈述（开场铺日常） | `in a low even voice at a conversational pace` |
| 回忆细节（讲书包、讲钱） | `in a low voice, the words coming a little faster` |
| 被戳中、想岔开 | `her voice lifts at the end, the words running together` |
| 硬撑、往下压 | `in a low voice that stays level, her throat moving once` |
| 松口、声音先垮 | `her voice thins out, the last words losing air` |
| 真正绷不住 | `a small broken voice, the words catching` |

**同一种语调描述最多用 2 段，第 3 段必须换。** 机器查法见 4.4。

### 3.5.3 哭不能突然：三拍 + 中间一个静止镜

`acting-recipes.md` 第四节原文：

> 转折要**三拍拆三镜**：第 1 拍压住 → 第 2 拍错位（假的那面裂开）→ 第 3 拍释放
> **中间必须有一个静止镜（1–2 秒，只写呼吸与眼神），否则转折没有重量。**

落到分镜：

| 拍 | 内容 | 写法 |
|---|---|---|
| 起（压住） | 还在撑 | `her brows pull together, her lips press thin` |
| 转（错位） | 假的那面裂开 | `the skin around her eyes starts to shake` |
| **停（静止镜，无台词）** | **凡哥要的「别太突然」** | `her eyes turn up, water gathers along her lower lids, her shoulders rise with a breath` |
| 落（释放） | 绷不住 | `the inner ends of her brows lift, her eyes squeeze shut, her mouth opens and her teeth show, her jaw shakes` |

**凡哥原话**：「后面当事人哭的太突然 前面情绪一直非常的平静」——缺的就是第 3 拍那个停。**这一镜要单独成段或单独成镜，不许和释放挤在一起。**

### 3.5.4 标点翻译成身体动作

台词里的标点不是语法，是呼吸和肌肉的时间表（`acting-listen.md` 第四节）：

| 标点 | 身体上是什么 | 写进镜行正文 |
|---|---|---|
| `，` | 半口气、视线落一下 | `she breaks off for half a breath, her eyes drop to the table` |
| `。` | 说完不立刻收表情，留一拍 | `her lips stay parted after the last word` |
| `……` | 气断在喉咙、话没说完 | `her breath catches, the words stop in her throat` |
| `（沉默）` | 眼神路径 + 呼吸 + 泄漏 + 余味 | `she holds his eyes, her jaw tightens, then she turns her face away` |

**台词里有几个「……」，镜行就该有几处「气断/停住」。**

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

### 4.4 表演层机检 `acting_check.py`（技能自带机检没有这一项）

`h3_lint.py` 30 项全绿，脸上照样可以一动不动 —— **它不查表演层**。2026-11-23 起补一道：

```bash
cd /d/Hermes/cache/emotion
python D:/Hermes/scripts/acting_check.py --all
```

| 查什么 | 判据 | 级别 |
|---|---|---|
| 四区动作 | 每段正文里眉/眼/口/颌有几区在动 | **<2 区 = 红**；恰好 2 区 = 黄 |
| 泄漏动作 | 有呼吸/吞咽类「在忍」证据吗 | 无 = 黄 |
| 省略号翻译 | 台词有 `……` 但镜行无「气断/停住」 | 黄 |
| 语调重复 | 同一种 `says in a ... voice` 出现几次 | **≥3 次 = 红** |

**红了不许提交**（脚本退出码 1）。`--all` 扫同目录全部 `seg*.txt`。

**实测《偏心》第一版：红 22 · 黄 7。** 修法见 3.5 节四条。

---

## 第 5 步 · 提交与合成

- 提交：`{"prompt": payload}`，`mode` 必须显式 `ref2va`，竖屏 `w=544 h=960`，成片统一放大到 810×1440。
- 参考图缩到 1024 宽；5 张 2848×1600 一起 VAE 编码会 `Fatal Python error: Aborted`。
- 12–14 秒一段，RTX 5080 Laptop 16GB 约 **10–15 分钟/段**（首段含 32B 文本编码器加载，更慢）。
- **队列会丢**：ComfyUI 重启后 pending 全没，跑前先 `curl -s http://127.0.0.1:18188/queue` 确认，别以为提交了就一定在跑。

### 5.1 长队列要盯着「多久没出新段」，不能干等（2026-11-22 白等 74 分钟）

**20 段连跑时，第 15 段整整 74 分钟没出片，我还以为「就是慢」，直到他问第三遍才去查 —— 一查是显存满了在拿硬盘当内存。**

**监控口径（跑长队列时每 10–15 分钟查一次）**：

```bash
ls -lat /d/SDkecheng/ComfyUI/output/*-audio.mp4 | head -4   # 最近 4 段出来的时间
date +%H:%M                                                 # 跟现在比
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
```

- **上一次出片距今 > 20 分钟** → 立刻查日志每步耗时，别等。
- **某一步耗时突然跳一个数量级**（实测 164 秒 → **2136 秒**）+ 显存 >90% → 显存打满，不是提示词问题。
- 处理：停队列 → 杀 18188 端口进程 → 确认显存归零 → 重启 → **只重交没跑完的段**（已出的不受影响）。详见 `av-generation-troubleshooting` 的 C-9。

**预防**：**每跑 10–12 段主动重启一次 ComfyUI**，比跑崩了再救便宜。

⚠️ **报时间要给依据，不许再按「平均 10 分钟/段」线性外推** —— 必须基于「上一段实际出来的时间」，并且说明「这个速度是最近的，前面有慢段」。他问了三遍"还有多久"，根源是我每次都拿平均值算、没查实际。

### 5.2 段跑出来先抽一张联系表，再往下砸时间

跑完全部段立刻拼一张 contact sheet（`av-generation-troubleshooting/scripts/contact_sheet.py`），一次看六段比对：

- **同一张脸吗**（六段里人物服装、发型、脸的轮廓是否一致）
- **同一个房间吗**（家具、窗、光的方向对不对）
- **关系对吗**（两人距离、朝向、有没有在对视）
- **闪回段是不是太暗**（实测老家闪回画成接近全黑，像苦情片，不像"平常的一天" → 后期提亮即可，不必重跑）

发现系统性问题（如童星参考图中性偏男）要先改图再重跑那几段，别等全部跑完。

⚠️ **改图还不够 —— 提示词里的文字赢过参考图。** 实测：把小女孩参考图从"齐耳短发"换成"歪马尾+碎花毛衣"后重跑，画面**仍是短发男孩**，因为 `subject_definitions` 里那句话还写着 `her chin-length black hair, her plain worn sweater`。H3 按文字画，把图当参考。

**重做某个角色时的动作顺序**：① 改图 → ② `grep -n "hair\|sweater" seg*.txt` 把所有描述旧外貌的句子找出来 → ③ 逐字改成新外貌（`subject_definitions` 与 `retention_analysis` 两处都要改）→ ④ 再重跑。只改图不改字，等于没改。

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

### 逐段验完还必须验整片（2026-11-22 收尾才发现的四类错）

**每段单独 ASR 全绿，拼起来仍可能三处出错。** 原因是这些错不在单段内部，而在"段与段的接缝"和"跨段重复"。**交付前必须对成片再转写一次，把 60+ 句按序打印出来逐行看。**

| 症状 | 真因 | 改法 |
|---|---|---|
| **同一句出现两遍**（58.8「好像没有」+ 62.0「好像没有」） | 我自己把这句同时写进了段06 结尾和段07 开头。覆盖核对只查"原稿有没有漏"，查不出"多出来一次" | 删掉后一段那句，**段长和镜数一起改**（3 镜 8 秒 → 2 镜 5 秒），重跑 |
| **模型自己重复一遍**（段12「奶奶走的时候」念两次，提示词里只有一处） | H3 生成时的自发重复，不是稿子错 | 原提示词不动，**直接重跑这一段**，大概率就好了 |
| **某句听不到**（「对不起」整句缺失，只剩对方「不用道歉」） | 我写的是 `has her hand pressed flat over her own mouth ... says through her hand` —— 手捂嘴，声音被闷掉 | 让手先放下再说：`Her hand drops away from her mouth. She says in a small broken voice:` |
| **某句念成同音别字**（弟→的、嘛→吗、哦→嗷） | **多半是 ASR 听错，不是片子错。** 短句无上下文时 faster-whisper 判断同音字很差 | 不要立刻重跑。先看这句是否"说话人/语义上只能是原字"；`嘛/吗`、`哦/嗷` 这类必然误判，放过。只有真影响语义的（`我弟` vs `我的`）才值得重跑一次 |

**判重复的口径**：整片句数 vs 剧本句数。49 句剧本拼完应该是 ~68 个 ASR 断句（长句会被切碎），**但任何一句原文只能出现一次**。逐行扫，不要只看总数。

**收尾顺序**：整片 ASR → 改 Prompt → 只重跑出错的那几段 → 重拼 → 再整片 ASR 确认。别从第一段重来。

---

## 支持文件

| 文件 | 用途 |
|---|---|
| `scripts/lint_all_segs.py` | 按段表批量跑 h3_lint，汇总 FAIL/WARN |
| `scripts/check_dialogue_coverage.py` | 台词原稿 vs `<d>` 块覆盖核对，揪出拆句丢句 |
| `scripts/audit_final_film.py` | **成片审计**：转写整片 → 逐行时间轴 + 重复句 + 漏句 + 语言判定。交付前必跑，逐段绿不代表拼起来没问题 |
| `references/lint-pitfalls.md` | 机检常见项的完整对照（含原文与改后写法） |
| `references/case-2026-12-19-pianxin.md` | 《偏心》全废与重做实录：三小时素材作废的完整因果 + 收尾四处返工 |

**外部脚本（不在本技能目录，但每次必跑）：**

| 脚本 | 用途 |
|---|---|
| `D:/Hermes/scripts/skill_full.py` | **技能读全器**：`--read` 一次摊开全部文件、`--audit` 全库体检标高危。见第 -1 步 |
| `D:/Hermes/scripts/acting_check.py` | **表演层机检**：四区动作 / 泄漏动作 / 省略号翻译 / 语调重复。见 4.4，红了不许提交 |

---

## 主控台登记

改本技能后同步 `DASHBOARD.md` 与 `skill-router` 路由表。
