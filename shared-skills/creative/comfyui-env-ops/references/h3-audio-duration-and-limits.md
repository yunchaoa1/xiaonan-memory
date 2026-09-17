# H3 工作流的音频路线与时长上限（源码级事实 + 两套口径）

> 2026-09-15 采集。源码 = 本机 `ComfyUI/custom_nodes/ComfyUI-MiniMax-ContextIR/`；UI 实证 = 凡哥截图。

---

## ⚠️ 第一条：云端 API 限制 ≠ H3 通用限制（凡哥 2026-09-15 当场纠正）

我把「单次音频 ≤15 秒」当成 H3 的通用规矩写进了文档，凡哥直接甩截图纠正：**本地 media loader 能载入整首 2:30 的母带并任意剪辑**。

- **云端 API 口径**：音频单请求总长 ≤15 秒（超了被拒 `total audio duration 24138 ms exceeds 15000 ms`）→ 用 API 做 MV 的人**必须切歌**。
- **本地开源权重口径**：`MiniMaxH3MediaLoaderFantastic` 可放整首、任意段剪辑 → **不受此限**。

**纪律**：写任何「上限/限制」前先分清**是哪一层**（云端 API / 本地开源权重 / 模型本身 / 工作流节点参数）。别把平台限制写成模型限制——这类错误会直接改变方案骨架，凡哥会当场发现。
同样适用于其他平台：**凡哥机器上看得见的东西，优先信他的截图**，别拿文档里的 API 限制跟他争。

---

## 生成时长由谁定（源码级）

| 事实 | 依据 |
|---|---|
| 每次生成的时长 = `MiniMaxH3ReferenceSplitter.duration`，**Float 1..15 / step 0.01** | `h3_context_ir.py:369` |
| 落到执行时**取整为 1-15 整数** | `h3_context_ir.py:459` `int(min(15, max(1, floor(duration+0.5))))` |
| **我们这版设 `duration=15`** → 每次生成 **15 秒 / 362 帧 @24fps**（实际 15.08 秒） | 工作流 `#221`；`h3_unified.py:55 duration_to_length`（`max(5, round_half_up(duration*fps))`） |
| ⚠️ **上面这个 15 是怎么定的**：同一节点 `widgets_values_named`（按名）里写的是 **9**、`widgets_values`（按位数组）里是 **15** —— **UI 格式 JSON 的参数存两份、两处会不一致，实际生效的是数组值**（2026-09-15 由 UI→API 转换器输出复核确认）。**别只读 named 那份就下结论**（本文件初版即因此写错成 9 秒，连带把「2:30 的歌 ≈ 17 镜」也算错；按 15 秒/镜应为 **≈10 镜**） | 工作流 `#221` |
| 生成本身的音频 latent 长度 = 生成时长（`audio_latent_t = round(duration × AUDIO_LATENT_FPS)`） | `h3_unified.py:80-81 temporal_shape` |
| **目标音频 latent 是零初始化** → **输出音轨由模型自己生成**，不等于参考音频 | `h3_unified.py:116` `audio = torch.zeros((1, 32, 2, audio_t))` |
| 参考音频**只作条件**（喂给模型，不是输出音轨） | `h3_unified.py:147 _encode_reference_audio` |
| `MiniMaxH3AudioLock`（把参考音频锁成输出音轨）**在本版是 bypass**（`mode=4`） | 工作流 `#226` |

**推论（未实测）**：本版成片的音轨是**模型生成的版本**，不是原曲；要「最终 MP4 音轨 = 原曲」需后期替换，或启用 AudioLock（属改工作流，需凡哥拍板）。

---

## 音频输入路线

1. 媒体加载器读文件：`h3_media_io.load_audio(file, start=_trim(i)[0], end=_trim(i)[1])`；视频轨走 `extract_audio(...)` —— `h3_fant_nodes.py:181-189`
2. **`start`/`end` 在采样前裁剪源，只有保留段被解码**（原文：`start`/`end` (seconds) trim the source before sampling; only the trimmed span is decoded, so trimming a long file is cheap）—— `h3_media_io.py:312-313`
   → 所以「放整首进去」是可行且开销小的
3. UI 就是那个波形编辑器：`+Segment / −Segment / Use segment / Apply`，`nudge 0.1s（+shift = 1s）`、`[` / `]` 设起止点
   （凡哥截图：`爱的记忆.mp3` 全曲 2:30、`0.00 → 149.98`、**`150.0s kept`**）
4. 下游：`ReferenceSplitter` 输出固定槽位（音频在索引 15 `audio_1`）→ `MiniMaxH3UnifiedToVideo` 的 `ref_audios.ref_audio_0` + `MiniMaxH3AudioLock`

---

## 云端 API 口径对照表（第三证据，仅当参考）

来自 Atlas Cloud 的付费实测文章（🟢 对 API 有效，**不可直接套到本地**）：

| 项 | API 限制 |
|---|---|
| 单次生成 | 4-15 秒（15 秒是**单次上限不是项目上限**） |
| 素材总量 | 图 ≤9 ｜ 视频 ≤3（各 2-15s）｜ 音频 ≤3（各 2-15s）｜ **合计 ≤12** |
| 音频 | 不能单独送（须配图或视频）；单请求内**音频总长 ≤15 秒** |
| 参考音频计费 | 免费（只按输出秒计费） |
| 提示词 | ≤7,000 字符；**无独立负向提示词字段** |
| 分辨率 | 768p 探索 / 2K 交付；长宽须 32 倍数 |

**切镜铁律（🟢 实测）**：5 秒 = 1-2 镜 ｜ 10 秒 = 2-3 镜 ｜ 15 秒 = 3-4 镜。**切得越多，每次剪切都要重新匹配参考 → 脸越容易漂。**

---

## ✅ 已定论：走 **A 路线 —— 音频不切，只切画面**（2026-09-15 读源码解决，不用跑）

**问题**：整首 2:30（保留 150s）放进加载器后，模型是「整轨做条件、只生成 N 秒画面」，还是「只取前 N 秒」？

**答案 = A（整轨做条件）。** 依据 `h3_unified.py:531-537`：

```python
for index, audio in enumerate(ref_audio_values, 1):
    encoded_audio, audio_t = _encode_reference_audio(audio_vae, audio)   # ← 按音频自身长度编码
    real_ref_items.append({"type": "audio"})
    real_ref_blocks.append({"kind": "audio", "ref_audio_t": audio_t, "audio_latent": encoded_audio})
```
- 参考音频**按自身实际长度整段编码**成参考块，**不被 `duration` 截断**
- `duration` **只**决定**目标**帧数（`h3_unified.py:652`）
- 素材上限只管**个数**（图≤9/视频≤3/音频≤3），**不管时长**

**推论**：口型不会遭遇「切片偏移累积」（那是切歌派被 API 逼出来的通病，与我们无关）→ **我们的分镜只需按画面切，音频一路连着。**

### ⚠️ 仍有两个保留（别把定论说过头）
1. **长度外推风险**：模型大概率没在 150 秒参考音频上训练过 → **结构上支持，效果未知**。建议先用 30 秒试再推整轨。
2. **输出音轨不是原曲**（见上表：目标音频 latent 独立、零初始化、长度=duration）→ 要原曲音轨需**后期替换**或**启用 AudioLock**（`#226` 改 mode=0，属改工作流、需凡哥拍板）。

## 验证一次要看的四件事

1. 输出音轨是**模型生成的**还是**原曲**（听 / 看波形）
2. **口型是否对得上、是否全程稳**（长参考音频的实际质感 —— 上面第 1 条保留只能靠真跑回答）
3. 16G 显存下**二采（latent 放大 1.5× + TiledSampler）会不会 OOM**（云端 5090 32G 无此压力）。
   ✅ 一采已过这道关、**二采没过**（见下方「首跑实测结果」）：日志 `Model MiniMaxH3 prepared for dynamic VRAM loading. 19995MB Staged` —— **20GB 级 int8 主模型在 16GB 显存上靠动态装载撑住了**，「模型比显存大必 OOM」不成立，别据此劝退。
4. 日志里加载器实际取了多少秒音频

## 🎬 首跑实测结果（2026-09-15，15 秒 / 齐白兰四视图 + 爱的记忆全曲 149.98s）

| 待验问题 | 答案 |
|---|---|
| 一采出片了吗 | ✅ `output/H3/MV-实测1-一采_00001-audio.mp4` = **960×544 / 15.083s / 24fps / AAC 32kHz 双声道 / 3.8MB**，耗时 **≈4.5 分钟** |
| 输出音轨 | AAC 32kHz 双声道**随生成一起出来了**；是否与原曲逐帧一致**未比对**（按上表源码事实应为模型生成版）→ 成品要原曲音轨仍须后期替换或启用 AudioLock |
| 口型 | 画面有演唱口型（收尾帧嘴张开）✅；**跨镜累积偏移无从判断**（本次只跑 1 个 15 秒片段，没跑多镜） |
| 20GB 模型在 16GB 显存 | ✅ 动态装载撑住（`19995MB Staged`），**一采全程没 OOM** |
| **二采（放大 1.5× + TiledSampler）** | ❌ **OOM 崩了** —— 见下 |

### ❌ 二采 OOM 根因 = `bypass_tiling`，不是「显存就是不够」

```
12:10:58  Requested to load MiniMaxH3 → 19995MB Staged      ← 二采重新装载 20GB 模型
12:14:48  aimdo: src/hostbuf-file-reader.c:92:ERROR:hostbuf_file_reader_read:
          device copy failed result=2 size=1376256 device=0  ← 权重搬运时崩
          !!! Exception during processing !!! aimdo memory compile error
          torch.AcceleratorError: CUDA error: out of memory
```

**根因**：`#1330 MiniMaxH3TiledSampler` 的 **`bypass_tiling=True`**（tooltip 原文「不分块。」）
→ 二采把整张 1440×816 **一次性**塞进显存 → 峰值爆掉。云端 32G 跑得动，16G 不行。

**修法**：`bypass_tiling=False` + `n_tiles=2` + `tile_overlap=16` + `refine_seams=True`。
相关旋钮语义（`h3_tiled_sampler.py:252-260`）：`n_tiles` 分块数 / `tile_overlap` 重叠宽度 /
**`max_size_for_no_tile` = 自动不分块阈值**（轴尺寸 ≤ 该值则仍不分块；本机设 32，1440→latent 90 > 32，所以会真分块）。

⚠️ **别草率归到 aimdo+sage 已知 issue（#16144/#15759）上结案** —— 先看该节点的 `bypass_tiling` 取值。

### 💡 由此定下的 16GB 生产策略

**一采先出片定稿（960×544 已够审画面与口型）→ 全片统一做二采放大。**
不必每镜硬扛二采，16G 机器也能做完整支 MV。

## 相关

- MV 制作方法论（Treatment → Storyboard → Shot List，社区/业界现成做法）：`ltx-video-prompt` 的 `references/mv-production-methodology.md`
- 工作流缺件/模型清单：本 skill 的 `references/h3-opc-delivery-workflow.md`、`references/h3-model-sourcing.md`
