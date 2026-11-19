# H3 Ref2VA 无头跑片配方（2026-11-19 实测跑通）

> 场景：手里有写好的 H3 官方六段式提示词 + 一套资产图，要**不经过 GUI**、**不被工作流里的改写节点污染**，直接出片。
> 环境：本机 RTX 5080 Laptop 16G，ComfyUI 0.35.0，`D:\SDkecheng\ComfyUI`，端口 18188。
> 结论：**跑通了**（11.54 秒 / 1440×832 / 带音轨），但踩了四个坑；下面是可复现的完整路径。

---

## 一、流程总览

```
UI 工作流 json ──(object_info 驱动)──> API payload
                                        ├─ 展开子图（subgraph）
                                        ├─ 删掉提示词改写链
                                        ├─ 参考图 LoadImage 直连
                                        ├─ mode 显式 ref2va
                                        └─ 提示词设为常量
                                        ↓
                                  POST /prompt
```

启动：`cd /d/SDkecheng/ComfyUI && ./.venv/Scripts/python.exe main.py --port 18188 --listen 127.0.0.1`
就绪判据：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18188/system_stats` → `200`。

⚠️ 启动日志里 ComfyUI-Manager 拉 `raw.githubusercontent.com` 失败的 Traceback **不是故障**（墙），节点照常加载。**别把它当崩溃证据。**

---

## 二、UI → API 转换（自写，零依赖）

`/object_info` 单类型查（全量会超时而 curl 写盘报 exit 23）：`GET /object_info/MiniMaxH3UnifiedToVideo` → 3.5KB。
全量用 python `urllib` 拉，1904 个类型。

**转换规则**：
- 每个 node → `{"<id>": {"class_type": type, "inputs": {...}}}`
- widget 值按 `object_info` 的 `required`→`optional` 顺序取，`INT/FLOAT/STRING/BOOLEAN/枚举(数组)` 算 widget，`CLIP/MODEL/LATENT/...` 算连线
- 连线覆盖：`node.inputs[i].link` → `links[id]` → `[str(origin_id), origin_slot]`
- UI-only 节点（`MarkdownNote` / `ShowText|pysssss` / `Fast Groups Bypasser`）跳过

**⚠️ 动态控件陷阱（最容易翻车）**：`COMFY_DYNAMICCOMBO_V3` 在 `widgets_values` 里占多格（主值 + 子参数），按 `object_info` 顺序数会整体前移一格。实测症状：

| 节点 | 错位后 | 正确 |
|---|---|---|
| `BlockSparseAttention` | `end_percent=1.3`（>max 1.0）`start_percent='sol-attn'` | `selection='sol-attn'`, `start_percent=0.2`, `end_percent=1.0`, `dense_blocks=''`, `min_tokens=12288`, `extra_tokens=256`, `sink_conditioning='exact_kv_and_rows'`, `verbose=False` |
| `MinimaxH3LatentUpscaler3D` | `align='scale by multiplier'` | `mode='scale by multiplier'` + **`"mode.scale": 1.5`** |
| `MiniMaxH3ReferenceSplitter` | `duration='16:9 (Widescreen)'` | `aspect_ratio='16:9 (Widescreen)'`, `duration=11.0` |

**判据**：报错里出现 `value_bigger_than_max` / `value_not_in_list` 且值明显不合理 → 九成是动态控件错位。**对这类节点直接手写完整 inputs，别信自动映射。**

**动态子参数的点号写法**：报错原文是 `Required input is missing: scale` / `extra_info.input_name: mode.scale` → payload 里必须写 `"mode.scale": 1.5`。

---

## 三、子图（subgraph）展开

0.35 的工作流里会有 `type` 是 UUID 的节点（本例 `1297` = "模型加载"组）。它不在 `/object_info` 里，转换器会跳过 → 报 `KeyError: '1297'`。

展开方法：
1. 从 `wf['definitions']['subgraphs']` 取那 12 个内部节点，id 加前缀（`sg_127` / `sg_1221` ...）避免冲突
2. 内部 links 照搬（`origin_id`/`target_id` 都不是 `-10`/`-20` 的那些）
3. 输出映射看 `sg['outputs'][i]['linkIds']`：`MODEL→1369`、`MODEL_1→1371`、`CLIP→128`、`VAE→119`、`VAE_1→120`
4. 主图里所有 `['1297', N]` 改指到对应内部节点

说明：`MiniMax-H3` 的 UNET 走 `UNETLoader → MiniMaxH3SigmaShift → MemoryEfficientSageAttentionPatch → ModelAttentionBackend → BlockSparseAttention`，两条链（一采 / 二采）各一套。

---

## 四、★ 绕开提示词改写链（凡哥明确要求）

工作流里提示词的真实走向：

```
220 MediaLoaderFantastic(media_state: 图+文本)
   → 221 ReferenceSplitter
      ├─ slot 18 (string_1，原始文本) ─────────────┐
      └─ slot 0/1/… (picture_N)                    │
                                                    ↓
   221 slot18 + 5 个 system prompt ──> 1379 QwenTE_ImageInfer（Qwen 改写）
                                         ↓
                                    1301 Any Switch(slot0) → 201.prompt
   221 slot18 ─────────────────────> 1301 Any Switch(slot1)   ← 作者预留的直通
```

`1379 QwenTE_ImageInfer` 配 5 个 `PrimitiveStringMultiline`（T2VA / I2VA / L2VA / FL2VA / **Ref2VA** 各一套 "You are an expert MiniMax H3 … prompt engineer"），会拿你的六段式当"原始想法"重写一遍 —— **终稿会被洗掉**。

**绕法（两步）**：
1. `201.prompt` 设为**常量字符串**（直接塞六段式正文），不引用任何节点
2. 把 `1301 / 1379 / 1380 / 1382 / 1383 / 1384 / 1385 / 1386 / 1387 / 1378 / 1300` 从 payload 删除

删干净后 `1300 ShowText` 和 `1378 ShowText` 也会因引用被删节点而报 `KeyError`，一并删。

**收益**：提示词 100% 原样进模型；Qwen 15GB 文本编码器不加载，显存和时间都省。

---

## 五、参考图与采样链路简化

**不用 220/221 那一对**。`ref_images` 是 `COMFY_AUTOGROW_V3`，直接上 N 个标准 `LoadImage`：

```
LoadImage(s1.jpg) → 201.ref_images.ref_image_0
LoadImage(s2.jpg) → 201.ref_images.ref_image_1
...
```

（`220` 的 `media_state` 里 `"file": "minimax_h3/png [input]"` 不是目录 —— 那个节点会把选中文件压成一个固定名字的临时文件，很难批量构造，所以绕开它。）

**删 `226 AudioLock`**（无参考音频时没意义）：把 `125 SamplerCustomAdvanced.latent_image` 直连 `201.av_latent`。`1210 ComfySwitchNode` 的 `switch=False` 取 `on_false`（`253 VAEDecodeAudio`），所以 226 的音轨输出本来就没被用。

**★ `mode` 必须显式 `ref2va`**：取值 `['auto','t2va','fl2va','ref2va']`。
`auto` 会判成纯文本 → **参考图全忽略，任务 `status: success` 照样出片**，但人物长相、道具、场景全跑偏。**最阴的坑：不报错、有片子。**

**其他必须项**：`width=960, height=544, duration=<秒>, fps=24, ref_image_size='match'`。

---

## 六、参考图必须缩小（否则 VAE 解码崩）

**症状**：一采采样 6 步全部跑完（进度条 100%），然后 `Fatal Python error: Aborted`，栈：

```
vae.py line 258 in forward
vae.py line 302 in forward
vae.py line 393 in _decode_pixels
vae.py line 521 in tiled_decode     ← 崩在这
vae.py line 419 in _adaptive_decode
vae.py line 645 in decode_temporal
```

**根因**：ref2va 会把参考图过 VAE 编码，5 张 2848×1600（4.5MB）直接吃干净 16G。

**修法**：最长边缩到 1024、存 jpg q92（→ ~100KB）。
```
s1/s2/s3: 1024×575  ~100KB
s4/s5（竖版道具）: 768×1024
```
缩完一次通过。

**⚠️ 与既有的 `short_edge_max=0` 那条是同一类病的两个入口**：那条是二采侧未缩放，这条是 ref2va 编码阶段爆。**先缩图，再谈参数。**

---

## 七、实测工时与输出

| 阶段 | 分辨率 | 步数 | 耗时 |
|---|---|---|---|
| 一采 | 960×544 | 6 步 × 33 秒 | **≈4.5 分钟** |
| 二采（1.5×） | 1440×832 | 4 步 × 107 秒 | **≈8 分钟** |
| 合计 | | | **≈12 分钟 / 11 秒段** |

输出：`output/Minimax_00001-audio.mp4`（二采，`245`）+ `Test_S01_00002-audio.mp4`（一采，`227`）。
成片：960×544 或 1440×832，24fps，H264+AAC，11.54 秒。

**只验证镜头设计时只跑一采**（4.5 分钟），风格/画质是统一参数的事，四个候选技能跑偏得一样，不影响横向对比。

---

## 八、成片自检（每次必做）

用 `cv2` 提帧（`ffmpeg` 不一定在 PATH）：
```python
cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS)
for t in (0.5, 2.5, 5.0, 8.0, 10.5):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t*fps)); cap.read() → imwrite
```
必看四件事：
1. **该出现的人都出现了吗**（本次：0.5 秒只有男主是对的，女主 5 秒才进画 —— 先对提示词的 [Shot] 边界，别急着判失败）
2. **人物长相/服装对不对**（不对 = `mode` 判错或参考图没生效）
3. **道具对不对**（本次白瓷盖杯正确 = 道具参考图生效）
4. **末段有没有崩**（10.5 秒抽帧，别只看开头）

---

## 九、提示词侧的配套硬限制（本次实测得出，属于 `h3-video-prompt` 但那个技能 user-owned 改不了，先记这）

| 规则 | 数据 |
|---|---|
| **单镜 ≤70 词** | 70 内正常；>75 开始丢东西；**>100 直接丢指令，先丢机位** |
| **镜长决定词数** | 4.2 秒/镜 → 67–86 词（合规）；5.3 秒/镜 → 最高 119 词；**8.5 秒/镜 → 114–138 词，必爆** |
| **风格句不能省** | 六段式 `detailed_description` 开篇不写风格句 → 出片是**写实电影感**，不是国漫 3D（本次实测：人物/道具/场景全对，唯独风格跑偏） |
| **道具一件一张图** | 六宫格道具不行 —— `<Subject N>` 只能指一个主体；2816×1584 切 6 格每格 ~940×790，糊成"平均道具" |
| **场景用平视主视角** | 不用俯视图（H3 认不出"这是这个空间"，会自己补空间）。写"能同时看到 3–5 件固定陈设且都不出画"钉住 |
| **台词必须全量承接** | 漏台词**不报错、不告警**，静默丢；本次实测 zenstory 版漏了"我没跟别人说"，下一句逻辑就断 |

---

## 十、其他坑速记

- **vae 目录小写 `minimax-h3\`，unet/clip 大写 `MiniMax-H3\`** —— ComfyUI 的下拉列表是字符串精确比较，写错一个字母就 `value_not_in_list`
- **`1311 NumberCalculatorV2` 依赖 `221` 的 `duration`** —— 删 221 后要把 `a` 改成常量（`preview_frames = duration × 8`），或直接删它和下游 `1309 ModelPreviewOverrideKJ`
- **`226 AudioLock` 的 mode 只有 `lock` / `remix`**，没有 `off`，所以想"不锁"只能整个节点删掉
- **进程被外部 SIGTERM 杀过**（uptime 3 分钟就 exit -15）→ 用 `terminal(background=true)` 挂上，别用 nohup（Hermes 会拒 shell 级后台包装器）
- **OOM 后必须重启 ComfyUI**，`prompt_worker` 线程死了队列会永远卡在"排队=1"
