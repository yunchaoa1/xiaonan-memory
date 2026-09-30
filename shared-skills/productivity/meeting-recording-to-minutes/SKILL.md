---
name: meeting-recording-to-minutes
description: 凡哥发会议录音/长音频要"会议记录＋待办"时用。本地 large-v3 转写 → 结构化纪要 → 待办表。
version: 1.0.0
author: 小南
license: internal
platforms: [windows]
metadata:
  hermes:
    tags: [会议, 转写, 纪要, 待办, faster-whisper, 本地]
    related_skills: [project-topology-diagrams, project-dashboard, media-learning]
---

# 会议录音 → 会议记录 ＋ 待办事项

凡哥丢来一个会议录音（`@file:...m4a`，常在工作区外），要的是**会议记录 + 待办统计**，并且
「**你也要参与进来**」＝记录里必须单列**小南自己的任务**。全程**本地转写，不出网**（会议含战略/融资/法律内容）。

**实测基准（2026-09-30，写死当预期）**：72 分 48 秒 / 78MB m4a → 1871 段 → **GPU 转写 18 分钟**（≈4× 实时）→ 记录 1.8 万字 + 12 条待办 + 5 条我的任务。

## When to Use

- 凡哥发录音/视频文件 + 「做一个会议记录」「统计出待办事项」「你也要参与进来」
- 任何 **>10 分钟**的中文长音频要成稿（短教程视频另见 `media-learning` §2b 的双线对齐）
- 会上定了框架，要转成给团队对齐的文档（那一步接着走 `project-topology-diagrams` 出脑图）

## 总览（五步，别跳）

```
① ffprobe 看时长 → ② ffmpeg 转 16k 单声道 wav → ③ faster-whisper large-v3 后台转写（边跑边读）
→ ④ 分段读稿、按议题归档 → ⑤ 出 .md 纪要 + .docx + 待办表 + 我的任务表
```

### ① 看文件（先看时长再决定要不要跑）

```bash
cd /d/Hermes/attachments && ffprobe -v error -show_entries format=duration,bit_rate,size \
  -of default=noprint_wrappers=1 "9月30日.m4a"      # → duration=4369.66 (≈72.8 分钟)
```
附件常在 `D:\Hermes\attachments\`（报 "path is outside the allowed workspace" 不用管，**terminal / read_file 照常能读写 D 盘**）。

### ② 转音频（native 程序吃原生路径！）

```bash
mkdir -p /d/Hermes/cache/audio
ffmpeg -y -v error -i "9月30日.m4a" -ac 1 -ar 16000 -c:a pcm_s16le "D:/Hermes/cache/audio/meeting_16k.wav"
```
⚠ **MSYS 路径不被转换**：给 ffmpeg 的输出路径要写 `D:/...` 正斜杠原生路径，写 `/d/...` 会 `exit 127`。

### ③ 转写（脚本＋本地模型）

模型已下好常驻：`D:\Hermes\models\faster-whisper-large-v3`（2.9G，**复用，别再下**）。没有时才取（huggingface.co 本机不通，**走镜像**，约 90 秒）：

```bash
HF_ENDPOINT=https://hf-mirror.com python -c "
import os; os.environ['HF_ENDPOINT']='https://hf-mirror.com'
from huggingface_hub import snapshot_download
snapshot_download('Systran/faster-whisper-large-v3', local_dir=r'D:\Hermes\models\faster-whisper-large-v3',
                  allow_patterns=['*.bin','*.json','*.txt','*.md'])"
```

跑转写（**后台 + notify**，别前台干等 18 分钟）：
```bash
cd /d/Hermes/scripts && python transcribe_meeting.py        # 见 scripts/transcribe_meeting.py
```
关键参数（都在脚本里，改文件名即可复用）：`device="cuda"` / `compute_type="float16"` / `language="zh"` /
`beam_size=5` / `vad_filter=True` / `condition_on_previous_text=False` /
**`initial_prompt`＝人物·项目术语表**（谢泽凡/何锦波/吴伟俊/李林/唐光辉、OPC、影剧工坊、智提分、浪浪河…）——
术语表对中文会议**准确率提升最大**，且**逐段写 txt+json**，所以能边跑边读。

### ④ 边跑边读（不要等它跑完才开始干活）

- 转写脚本**每 20 段 flush 一次**到 `.txt`（带 `[起-止]` 时间戳），用 `read_file(offset=…, limit=420)` 分批读（一次约 400 行 ≈ 17KB，全文约 1900 行）。
- 读的时候就把内容往议题上归：**战略/管理/项目/风险/人事**，并记下**时间戳区间**（写进纪要，便于回溯）。
- 别把整篇一次性塞进上下文：**分批读、边读边定结构**。

### ⑤ 出三份东西

1. `会议记录.md`（结构见 `references/meeting-minutes-format.md`）→ 2. 同名 `.docx`（凡哥要转发）：
```bash
python D:\Hermes\scripts\md2docx_meeting.py     # 见 scripts/md2docx_meeting.py（标题/表格/加粗/引用都转）
```
3. **待办表**（写在记录里 + 回复里再列一遍短表）：`事项 / 责任人 / 时间节点 / 验收标准`。

## 硬规矩（凡哥口径，逐条踩过）

1. **转写原文一字不删改**；记录里只**校正人名与项目名**，原文稿（`.txt`/`.json`）原样保留交付。
2. **ASR 存疑词不脑补**：听不准的专有名词标 `[待确认]`，**在回复里点名问他**（实例 2026-09-30：「哈马斯」「LibTV/Lib」；会后要过一句"准确名字给我一下"）。项目名常被听错：影剧工坊→"影视/智聚/YouTube 工坊"、海螺 AI→"海罗"、RAGFlow→"Wrap Cloud"、ComfyUI→"CoverUI" → 用 `initial_prompt` 术语表压这类错，并建 `references/meeting-minutes-format.md` 里的校正表。
3. **归属＝会上明确认领 / 本人陈述**；没人认领写「待认领」，**禁止按岗位推定**（与日报口径「谁写＝谁做」分开记，记录里注明来源）。
4. **「你也要参与进来」**＝记录末尾必须有一张 **小南任务表**（我能独立做的打底稿/统计/技能化，别只列别人的活）。
5. **决议 vs 提议分开**：会上吵过但没定的事写"待定/未决"，**不要写成决议**；凡哥说"你说说看"的段落属于讨论。
6. **敏感内容如实记、不外发**：融资时间表、开源模型商用风险/授权策略、薪酬与考核思路 → 记录里保留，交付物只给凡哥，**不进共享区、不写进 Team 文档**。
7. 会议里凡哥交办给**数字员工/我的话**（例："录音→转文字→总结要点→结合项目分析"）→ 这既是记录内容，也是**我的能力清单**：如实标"已跑通/待做"。

## 坑

- **中文长音频别用 CPU medium**（`media-learning` §2b 是给 ≤2 分钟短教程的）→ 70 分钟会磨到失去意义；用 GPU large-v3。
- **模型/下载**：`huggingface.co` 本机不通 → 一律 `HF_ENDPOINT=https://hf-mirror.com`；不要在这条路上反复试直连。
- **ffmpeg / python 等 native 程序**：路径写 `D:/...`，不写 `/d/...`（MSYS 不转换 → exit 127）。
- **别前台等**：转写放后台 + `notify=true`，同时分批读稿（同一轮里 wait → read 交替）。
- **音频别留在 cache**：跑完删 16k wav（实测 134MB），**模型留着复用**；原录音归凡哥（`D:\Hermes\attachments\`）。
- **长会一定有"重复讨论同一议题"**：按**议题**归并、不按发言顺序流水账（例：考核量化在 28–45 分钟反复出现 → 合成一节）。
- **会议里的数字/日期是承诺，不是事实**：写进待办时保留"会上说的"，并与台账/总控台交叉核对，冲突就问。

## 验证

- [ ] 转写段数 × 时间戳：最后一段 `end` ≈ `ffprobe` 时长（2026-09-30：1871 段 · 72:48）→ 没漏尾。
- [ ] 记录里每条关键结论带**时间戳区间**，可回溯录音。
- [ ] `.docx` 能被 `read_file` 抽取出正文（表格/标题都在）；`ls -lh` 看体积正常。
- [ ] 待办表的责任人与会上认领一致；未认领项显式写「待认领」。
- [ ] 总控台（DASHBOARD）已记这场会（结论 + 待办指向）+ git 提交推送。

## 支撑文件

- `scripts/transcribe_meeting.py` — 转写主脚本（顶部改文件名/AUDIO 路径即复用；含术语表 `initial_prompt`、逐段 flush、进度打印）
- `scripts/md2docx_meeting.py` — 纪要 Markdown → Word（标题/表格/加粗/引用；微软雅黑，表格套内置样式）
- `references/meeting-minutes-format.md` — 纪要骨架模板 + 待办表字段 + **ASR 术语校正表** + 2026-09-30 实测实例与存疑词清单
- 关联：`project-topology-diagrams`（会上定的框架→XMind 脑图）、`project-dashboard`（总控台）、`media-learning`（短教程视频的双线取流）
