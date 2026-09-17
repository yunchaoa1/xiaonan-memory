# 无头提交：把 UI 格式工作流真正跑起来（2026-09-15 本机实测）

> 目标场景：凡哥说「**你来自己跑**」，而 ComfyUI 的 GUI 够不着（预览面板无响应、
> 桌面窗口枚举不可用）。此时唯一的路 = 把 UI 格式工作流转成 API 格式后 `POST /prompt`。
> 配套脚本：`scripts/ui2api.py`（转换 + `--submit`）。

## 0. 先确认三条事实，别在错的方向上耗

| 事实 | 实测 |
|---|---|
| UI 格式提交给 `/prompt` | ❌ `HTTP 500 … Server got itself in trouble`（`nodes`/`links`/`definitions` 顶层键服务端不认） |
| API 格式是唯一入口 | ✅ `POST /prompt` body = `{"prompt": {<node_id>: {"class_type","inputs"}}, "client_id": "<uuid>"}` |
| 服务端不做 UI→API 转换 | 子图（`definitions.subgraphs`）是**纯前端概念**：`execution.py` 里的 `has_subgraph` 讲的是「节点返回值里带图」，与工作流子图无关 |

GUI 两条备选路都不通时（本次都试过：`read_preview` / `drive_preview` 超时、`read_window_below` 报枚举不可用），**直接写转换器**，不要反复试 GUI。

## 1. 转换器要干的四件事（缺一不可）

1. **子图拍平**：`definitions.subgraphs[*].nodes` → 顶层，id 加 `sg` 前缀防撞号；再把顶层里指向子图实例的链接改指到内节点。
2. **bypass/静音节点同类型直通重连**：见 §3，漏了这一步 = 断链不出片。
3. **可达性剪枝**：从输出类节点（`VHS_VideoCombine`/`SaveVideo`/…）反向回溯，只保留这条链上的节点。
   本次 42 顶层节点 + 13 子图节点 → **33 个**（自动剪掉整条 Qwen 提示词支路和二采模型链）。
4. **下拉值归一化**：见 §4。

## 2. UI 格式的结构陷阱（写转换器前必须知道）

| 陷阱 | 实测证据 |
|---|---|
| **顶层 `links` 是数组，子图 `links` 是字典** | 顶层 `[231, 129, 0, 125, 0, "NOISE"]`；子图 `{"id":8919,"origin_id":1221,"origin_slot":0,"target_id":1250,"target_slot":0,"type":"MODEL"}` → 两种都要吃 |
| 子图内部的「虚拟输入槽」是**负数 id** | `{"id":8949,"origin_id":-10,…,"target_id":127,"target_slot":0,"type":"COMBO"}` = 该装载器的 widget 被**提升**为子图输入 → **丢弃这条链接，用节点自己的 `widgets_values`**（后者才是界面上显示的值） |
| 子图实例的 `inputs[].link` 全是 `null` | 9 个提升项（`unet_name`/`shift_video`/…/`vae_name_1`）都是 widget 输入 → 实例的 `widgets_values` 因此不可靠，**内节点的 `widgets_values` 才是权威** |
| 子图输出槽 ≠ 有人用 | 本例 `MODEL_1`（二采模型）`links: []` → **整条二采模型链无人消费**（设计如此，不是漏接）→ 剪枝后 `sg1221/sg1222/sg1250/sg1370/sg1371` 全被丢掉，只剩一采链 |

## 3. ⚠️ bypass 节点「同类型直通」是成败关键

ComfyUI 的 `mode=4`（bypass）/`mode=2`（静音）语义 = **删掉该节点，并把「与其输出同类型的那个输入」接到原输出的下游**。转换器不做这一步，就是单纯删节点 + 删链接 → **下游输入凭空消失**。

**本次实例（致命）**：
```
#226 MiniMaxH3AudioLock (mode=4)
  in : av_latent[LATENT, link 369] , audio[AUDIO, 9034] , audio_vae[VAE, 8981]
  out: av_latent[LATENT, links=[372]] , audio[AUDIO, [8834]] , report[STRING]
#125 SamplerCustomAdvanced.latent_image ← 372
```
→ 272 的消费者必须改接到 **369**，否则一采采样器没有 latent。同理 `8834 → 9034`。
`rep: #1335 LoraLoaderModelOnly(mode=4)` = MODEL→MODEL 直通，天然安全。
`rep: #1379 QwenTE_ImageInfer(mode=4)` 没有 STRING 输入 → 链接直接删 → `#1301 Any Switch` 的 `any_01` 空出 → **自动回落到 `any_02`（原始文本）**，正是设计好的「润色关掉走原文」行为。

## 4. 下拉值归一化：`value_not_in_list` 大小写真的会拦

**本次实测推翻旧口径**（本 skill 曾记「VAELoader 传不存在的名字也 200 放行、大小写不必改」）：

```
#sg120 VAELoader: {"type":"value_not_in_list",
  "details":"vae_name: 'MiniMax-H3\\minimax_h3_audio_vae_fp32.safetensors'
             not in ['minimax-h3\\minimax_h3_audio_vae_fp32.safetensors', ...]"}
```
工作流写 `MiniMax-H3\`（大写），磁盘实际目录名是 `minimax-h3\`（小写）→ **提交被拦**。
（同一份工作流里 `diffusion_models/MiniMax-H3\...` 却没报错 —— 因为那个目录名确实是 `MiniMax-H3`。
即：**报不报错取决于该目录在磁盘上的真实名字**，不是「有的节点不校验」。）

**纪律**：提交前对每个组合框输入做 case/斜杠归一化（`ui2api.py` 的 `norm_combo`），
**不要**把「Windows 文件层不区分大小写」当成「校验层也会放行」。

## 5. widget 名↔值 配对的三种情形（决定参数会不会整体错位）

| 情形 | 处理 |
|---|---|
| 文件 `inputs[]` 里的 widget 条目数 == `widgets_values` 长度 | ✅ 直接用文件自己的顺序（能带出 dotted 名 `aspect_ratio.size1` / `mode.scale` / `ref_images.ref_image_0`，这些在 `object_info` 里查不到） |
| 数量不等，但 `object_info` 声明数 == 值数 | 回落 `object_info` 顺序。实例：`ShowText\|pysssss`（0 条目 vs 1 值）、`QwenTE_ModelLoader`（0 vs 15）、`PrimitiveStringMultiline`（0 vs 1） |
| 两边都不等 | 打印 ⚠ 让人看。实例：`RandomNoise`（1 vs 2，多的那个是 `control_after_generate`，无害）、`ModelPreviewOverrideKJ`（6 vs 7，末尾空串，无害） |
| **值本身是参数名** | 已知的 **widget 值损坏**形态（见 `references/035-node-migration.md`）。`VHS_VideoCombine` 的 `widgets_values` = `['frame_rate','loop_count','filename_prefix','format','pix_fmt',…]` → **整节点手工定死**（`frame_rate=24, format='video/h264-mp4', pingpong=False, save_output=True, filename_prefix=<自己起>`） |

> 位置的容错是概率性的：**提交后逐个复核关键节点的 `inputs`**（`#201`/`#221`/采样器/保存节点），
> 别指望一次性全对。本次 `#201 MiniMaxH3UnifiedToVideo` 复核出
> `ref_image_0 ← 221[0]`、`ref_audio_0 ← 221[15]`、`width/height ← 221[21]/[22]`、`duration ← 221[25]` —— 与手工推算的槽位索引完全一致 ✅（这是「转换器对了」的强证据）。

## 6. 节点代次不同 → `required_input_missing`

```
#221 MiniMaxH3ReferenceSplitter: [{"type":"required_input_missing","details":"short_edge_max"},
                                  {"type":"required_input_missing","details":"align_to"}]
  "dependent_outputs": ["227","245"]
```
云版旧节点只有 4 个 widget（`aspect_ratio` / `size1` / `size2` / `duration`），本机装的节点要 6 个
→ **去另一份新一点的工作流里抄这两个值**（本例 `short_edge_max=0`、`align_to=16`），写进 `OVERRIDES`。
**别猜值**——`dependency_outputs` 会告诉你谁在等它。

## 7. 提交与监控（可复制的收尾流程）

```bash
cd <ComfyUI> && <venv>/python scripts/ui2api.py <ui.json> api.json      # 先只转换，看诊断
<venv>/python scripts/ui2api.py <ui.json> api.json --submit            # 再真提交
```

提交前 `POST /free`（`{"unload_models":true,"free_memory":true}`）；轮询两处：
`GET /queue`（`queue_running` / `queue_pending`）+ `GET /history/<prompt_id>`（结束时 `outputs` 里给 `filename`/`subfolder`/`type`）。
进度看日志（`<ComfyUI>/user/comfyui_<port>.log`）：阶段行 `Requested to load X`、`Model X prepared for dynamic VRAM loading. NNNNNMB Staged`、收尾 `Prompt executed in …`。
第三方节点（tiled sampler / latent upscaler）**不上报进度** → 界面无进度条 ≠ 卡死。

**本次首次跑通的日志签名**（可当「链路通了」的判据）：
```
[MiniMaxH3 media_io] mp3: decoded via ComfyUI's own LoadAudio
Model MiniMaxH3TEModel_ prepared for dynamic VRAM loading. 14956MB Staged.
Model MiniMaxH3 prepared for dynamic VRAM loading. 19995MB Staged. 208 patches attached
```
→ 20GB 级 int8 主模型在 **16GB 显存**上靠动态装载撑住了（凡哥 5080 Laptop 16G）——「模型比显存大就必 OOM」不成立，别据此劝退。

## 8. media_state 条目结构（媒体加载器面板写入的那串 JSON）

`MiniMaxH3MediaLoaderFantastic` 的 `media_state` 是**字符串化 JSON 数组**，每条：
```json
{"kind":"picture|video|audio|string", "file":"minimax_h3/png [input]",
 "name":"齐白兰四视图.png", "duration":null, "width":1309, "height":736,
 "has_audio":false, "audio_mode":"off"}
```
- `file` 里的 `" [input]"` / `" [output]"` / `" [temp]"` 后缀由 `h3_media_io.py:56` 剥掉 → 解析到 `ComfyUI/input/minimax_h3/<名>`。
- 面板上传的实体文件落在 `ComfyUI/input/minimax_h3/<扩展名>`（如 `mp3`、`png`）——**云版存的是 `png_9122` 这类带随机数的名，本机就是 `png`** → 从别处搬来的 `media_state` 十有八九指向不存在的实体文件。**对策：先 `ls input/minimax_h3/` 看真实文件名，再改写 `file` 字段**（造个同名硬链接做双保险也很便宜）。
- 标签体系（`web/fant_medialoader.js` 的 `computeTags`）：`<Picture N>` / `<Video N>` / `<Audio N>` / `<String N>`，**各自独立编号**；`string` 条目**不占文件名额**（`fileCount` 里 skip）→ 图≤9 / 视频≤3 / 音频≤3 / 合计≤12 的口径只算文件类。
- 条目的 `audio_mode` 只对 **video** 条目有意义（`paired` / `standalone` / `off`），audio 条目上看到 `"off"` 属正常，别当配置错误。

## 9. 顺带体检：作者留的「模式开关」常常是全关的

同一份工作流里 `PrimitiveStringMultiline`（T2VA/I2VA/L2VA/FL2VA/Ref2VA 五条系统提示词）
**全部 `mode=4`** = 提示词优化链没有系统提示词可用（`Any Switch` 空转）。凡哥自己操作时按 `Ctrl+M` 连按很容易全静音。
**接手别人存的 UI 文件时，除节点/连线外还要 diff 一遍 `mode`**：本次 diff 出
① 两个 UNETLoader 指向**已被删除**的模型（`hybrid_b25-49` / `w4a8_mixed`）
② 放大倍率 2.0 vs 1.5
③ `#221` 少 2 个必需参数
④ 5 条系统提示词全静音
—— 这类「文件看着完整、一跑就废」的差异，只有逐节点 diff 才能发现（**用 `pyminimax` 的 `widgets_values` + `mode` 三元组比对**，见 `references/h3-opc-delivery-workflow.md` 的「多份相似工作流分辨判定法」）。

## 10. ⚠️ 崩溃会杀死任务线程：队列永久卡在「排队=1」→ 必须重启实例

**无头跑最容易被误判的状态**：监控看到 `queue_running=0, queue_pending=1` 长时间不动，
第一反应是「还没轮到 / 任务慢」，实际是**已经没人处理队列了**。

**机制**（2026-09-15 首跑二采 OOM 后实测）：
```
Exception in thread Thread-14 (prompt_worker):
  main.py:439 prompt_worker
  comfy/model_management.py:2094 soft_empty_cache
  torch.cuda.synchronize()  →  torch.AcceleratorError: CUDA error: out of memory
```
CUDA OOM 打死了 `prompt_worker`（**唯一处理队列的线程**）→ 之后**再提交的 `got prompt` 也没有人接**
→ `/queue` 永远 `pending=1, running=0`。**CUDA 上下文已坏，热恢复不了**（`/free`、`/interrupt` 都救不回）
→ **只能重启实例**。

**判据**：`/queue` 为 `pending≥1, running=0` **且**日志已停止增长（连续几次轮询无新行）。
`scripts/watch_prompt.py` 会把这种状态直接标成「⚠️ 卡死」。

**重启（Windows 本机实测）**：
```bash
netstat -ano | grep <端口>                        # 取真正持有端口的 PID（本机 18188 → 30740）
powershell -NoProfile -Command "Stop-Process -Id <pid> -Force"
cd /d <ComfyUI> && ./.venv/Scripts/python.exe main.py --listen 0.0.0.0 --port 18188 --disable-cuda-malloc
```
- ⚠️ **MSYS 下 `taskkill //F //PID x` 会把 `//F` 当字面量** → `ERROR: Invalid argument/option`；
  `cmd //c "taskkill ..."` 也会串味（会打出 cmd 版权头）→ **用 PowerShell `Stop-Process`**。
- ⚠️ 找 PID 别靠 `wmic process ... get CommandLine`（本机返回空）→ 用 `netstat -ano | grep <端口>` 监听行的最后一列。
- 重启后 `/queue` 自动清空（队列在内存里、不持久化），约 **50 秒**就绪（轮询 `/system_stats` 到 200）。

**缓存复用（⚠️ 只在「不崩」的前提下成立）**：`POST /free` 带 `free_memory:false` = 只卸模型、**保留节点输出缓存**。
只改了后段参数时用它，可跳过已跑完的前段（本例一采 4.5 分钟）。
⚠️ **但崩溃路径上这条没有用**：二采 OOM → `prompt_worker` 死 → **必须重启** → 内存里的节点缓存全没 → 下一次仍从一采重跑
（本例实测：`--nofree` 提交过，但那次任务卡在死线程上、最终仍需重启，一采每次重跑 = **每轮重试白花 4.5 分钟**）。
真想在 16G 上迭代二采，正解是**先把一采产物（latent）存盘**，再单独搭一条只跑二采的链去试——别靠缓存。

## 11. 二采在 16GB 上的实测边界（2026-09-15，**未解决**：照实记，别当配方用）

**✅ 一采（960×544 / 15s）稳定可复现，三次全成功**
```
output/H3/MV-实测1-一采_0000{1,2,3}-audio.mp4   各 ≈3.8MB
ffprobe: 960x544 / 24fps / 15.083333s / h264 + aac 32000Hz 2ch
耗时：got prompt 12:04:48 → 落盘 12:10:07 ≈ 4.5 分钟（含模型装载）
```
素材 = 齐白兰四视图（`minimax_h3/png`）+ 爱的记忆全曲（`minimax_h3/mp3`，149.98s 整轨，不切）

**❌ 二采（1440×816）三次全崩，日志位置完全一致**
```
12:10:58  Model MiniMaxH3 prepared for dynamic VRAM loading. 19995MB Staged. 208 patches attached.
12:14:48  aimdo: src/hostbuf-file-reader.c:92:ERROR:hostbuf_file_reader_read: device copy failed
            result=2 device_ptr=000000180CECB800 device=0 stream=… size=1376256
          !!! Exception during processing !!! aimdo memory compile error
          RuntimeError: hostbuf_file_reader_read failed  →  RuntimeError: aimdo memory compile error
12:14:49  Exception in thread Thread-14 (prompt_worker) … soft_empty_cache … torch.cuda.synchronize
          torch.AcceleratorError: CUDA error: out of memory
          Prompt executed in 00:10:00   （三次分别为 600 / 486.93 / 561.92 s）
```
三次改动 = 分块 / 分块+摘 sage patch / 分块+摘 sage+缩放 1.25（第 4 次结果未知，会话结束时仍在跑）。
**`free` 观测**：二采开始前 `VRAMdebug: free memory before: 11,798,177,280`（≈11.8GB 空闲，即一采结束后仍被占 ~4GB）。

**环境快照（判因用）**
- `comfy_aimdo` **0.5.3 生效**（`0.4.10` 的 dist-info 是残留）；`sageattention 2.2.0+cu130torch2.10.0andhigher.post6` 已装
- 启动参数 `--disable-cuda-malloc`（云端同款）；**未**使用 `--use-sage-attention`（sage 走的是工作流内的 patch 节点）
- 显存相关开关（`comfy/cli_args.py`，**均未实测**）：`--vram-headroom <GB>`（DynamicVRAM 额外保持的空闲量）、`--disable-nvml-pressure`、`--reserve-vram <GB>`、**`--disable-dynamic-vram`**（`enables_dynamic_vram()` 在 `--disable-dynamic-vram`/`--highvram`/`--gpu-only`/`--novram`/`--cpu` 任一存在时返回 False → 走经典离线调度）

**⚠️ 纪律**：以上是**已确认的观测 + 已证伪的修法**，不是「二采怎么修好」。下次接手先做两件事：
① 把一采 latent 存盘、搭单独的二采试跑链（把每轮成本从 ≈9 分钟压到 ≈4 分钟）；
② 一次只变一个变量，且**先记录改动前基线**（本 skill 曾把 `bypass_tiling` 写成根因，就是一次多变量+早下结论的后果）。
