---
name: av-generation-troubleshooting
description: 音视频生成出现杂音/画面异常时，用证据链（频谱/对照实验）排查根因，不猜不试错。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [troubleshooting, audio, video, comfyui, h3, diagnosis]
---

# AV 生成故障排查（Evidence-First Troubleshooting）

## When to Use

AI 生成视频/音频出现异常时（杂音、低频嗡、爆音、画面重复/分屏感、质量倒退），需要**定位根因**而不是试错重跑。也用于验证"某个环境因素是否问题根源"（如模型版本、框架版本、参数、提示词）。

## 铁律（凡哥 2026-09-03 明确纠正）

1. **先查官方 issue 和社区同病案例，再动手**——"别瞎猜瞎试，去官方找问题所在，精准处理"。GitHub issues（官方 repo + 插件 repo）和社区实测帖子往往已有根因+解决方案。
2. **对比排除法**：一次只变一个变量（版本/工作流/提示词/参数），设计对照实验，不盲目重跑试错。
3. **证据优先**：诊断结论要有客观数据（频谱、日志、时间戳、文件对比），不靠"听感+推测"下结论。
4. **别拿推测当结论**：因果链没做对照验证前，明确区分"实锤的事实"和"待验证的推测"。
5. **测试阶段只跑一采/最低成本路径**：能判定的最小产出（如一采带音频的 seg mp4）就够，不跑完整流程。
6. **工作流类故障：先去该工作流的 UP 主官方信息里找方案，再动手**（凡哥 2026-09-18 纠正：『你去看这个 up 主的官方信息，从那里找方案修，**不要自己瞎试**』）。
   - 「官方信息」三处优先级：① **UP 的视频教程**（讲工作原理与参数取舍）② **工作流 json 里的 MarkdownNote / 作者 B 站主页 / 网盘说明** ③ **插件源码**（节点参数定义、tooltip）。
   - 本次反面教材：在未看教程时自行推断出「cudaMallocAsync 分配器高压崩 → 加 `--disable-cuda-malloc`」，写进 skill 后被凡哥当场打回——真根因是 UP 早就讲过的「参考图不缩放会暴显存」。
   - **自创方案只能标"待验证"**，不得当结论写进 skill 或交付；**工作流身份也别凭印象**——从 json 的 MarkdownNote 读作者（本次实录：一直记成"小黄瓜"，实际是 **Astral星芒**）。

## 音频异常诊断：频谱法

**嗡声/杂音/爆音的判定不要只靠耳朵**，用频谱数据：

1. `ffmpeg -i <视频> -vn -acodec pcm_s16le out.wav` 提取音频
2. numpy FFT 分频段能量：<200Hz / 200-500Hz / 0.5-6kHz（人声区）/ >6kHz，加每 5 秒窗口主峰
3. 判据：
   - **嗡声**：无台词段也有 60%+ 能量在 <500Hz，人声区几乎为 0
   - **正常**：无台词段能量在中频（抽泣/水声/摩擦声）；台词段低频成分是**人声基频**（女声 165-255Hz、男声 85-180Hz）——低频占比高 ≠ 杂音，勿误判

可复用脚本：`scripts/audio_spectrum_check.py`

**注意**：先核对用户已有的实测事实（如"单段正常、多段杂音"）再归因——问题可能只在特定路径（长帧/多段/特定模式），不要轻易归到"模型能力"。

## 版本因素对照实验法

当怀疑"某框架/插件版本是根因"时，用**双版本独立部署**做对照（唯一变量=版本）：

1. 下载目标版本的独立安装（便携版/独立 venv），**不动现有生产环境**
2. 共享大模型文件（挂载/软链，不重下）
3. 复制必要插件 + 装同版本依赖（关键依赖版本照抄现有环境）
4. 同工作流、同 seed、同提示词各跑一次，对比输出
5. 判定后决定生产路径（切换版本 / 等官方修复合并 / 打官方补丁）

**镜像/托管环境警示（2026-09-09 实测教训）**：整体切 ComfyUI 版本前先查插件配对——预装镜像的 custom_nodes 常依赖特定小版本新增的 API（案例：LTXVideo 在 0.30.0 上 `ImportError: cannot import name 'interleaved_freqs_cis' from 'comfy.ldm.lightricks.model'`），降级后部分插件 import 失败、采样期直接原生崩溃（日志特征：尾部整段 `Extension modules: ...` dump + `Fatal Python error: Aborted`，且服务"端口起来了"但一 Queue 就死）。动手前用 `git diff <旧tag> <新tag> -- comfy/ comfy_extras/` 看后端差异：**小版本若只 bump 前端包（后端零差异），降级毫无意义**。

案例：H3 音频低频嗡的**干净版本 = 0.30.0 与 0.30.1**（两者后端 comfy/、comfy_extras/ 代码零差异，git diff 实锤；0.30.1 只是 bump 前端包）；嗡声在 0.30.2/0.31+；**官方最新 0.33.x 仍未修复**（#15799：音频恒定 DC/静音，试遍变量全失败）。**已验证的修复路线**：①Windows/本地 = 便携版 0.30.0 并存；②Linux 托管定制镜像整体降级 = 已实测失败（镜像插件配 0.30.1，切 0.30.0 后插件 import 失败、采样期原生崩溃 Fatal Abort）；③**云托管（智算云扉 waas）= 从基础 pytorch 镜像干净重建 v0.30.0+本地配套插件组合，2026-09-09 凡哥亲验 8s 一采无杂音 ✓**（完整命令链+平台机制+坑，见 `references/waas-cloud-h3-rebuild-case-2026-09.md`）。本地/旧镜像细节见 `references/h3-audio-noise-case-2026-09.md`。

**云平台机制先查官方文档（凡哥 2026-09-09 纠正："别瞎猜"）**：托管环境的镜像语义、自启机制、数据盘持久性、模板覆盖行为都**只有平台官方文档（如 docs.aigate.cc）+ 实测说了算**，不要拿通用 ComfyUI/Linux 经验脑补（实测教训：改 `/etc/waas-script/process-compose.yml` 加自启进程会被平台 entrypoint 开机模板还原）。平台文件系统分三类：持久数据盘（环境放这）、系统盘可写层（重启保留但 entrypoint 可能模板覆盖）、镜像层（重启还原）。

## 高清/2K 放大路线（2026-09-09 云端 32GB 实测教训）

**Director（AIMixer）refine upscale 到 2MP(1920×1088) 在 32GB VRAM = 物理 OOM**，逐层排查结论：
- h3_latent upscaler 官方 README 明说 **"saves time, not VRAM"**——放大后精修仍在目标分辨率跑，峰值 ≈ 直接生成高分辨率
- 换 pruned/nvfp4 小模型（staged 32.4→19.9GB、TE 25.8→14.9GB）后**仍 OOM** → 元凶是 2K latent 采样激活峰值，不是模型大小
- sageattention：**PyPI/tuna 最高只有 1.0.6**（无 2.x）；KJNodes sage 节点要 2.x 的 `sageattention.core`（1.0.6 无此模块 → "not new enough / could not determine CUDA architecture"）
- SolAttn(tau 1.2) 替代 sage 在 **3 步 refine 无效**（稀疏窗口 start0.2~end0.9 在 3 步中几乎不生效）
- turbo LoRA(4step v1.1_768p) + 2MP 大放大 = 细节修不动 → 成片比一采糊
- OOM 日志铁证行：`[WARNING] Segment 1 refine failed (Allocation on device); keeping last successful pass.`（= 静默回退一采放大结果，无精修）——凡哥看到的"直接出片、比一采糊"即此

**正解 = 绕开 Director，用官方原生模板**（ComfyUI 0.30.0 自带）：
- `MiniMaxH3ReferenceToVideo`（前端 Library→Video→"MiniMax H3：参考生视频"），参考图 ref_image_0..8 + 音频/视频参考，提示词=自然语言 + `<Picture N>`（非 Director 六段）
- 2K = ResolutionSelector megapixels 2.0 **直接一采生成**（无二采概念；流程=0.4 低清验收 → 同 seed 拉 2.0 重跑）
- 模型最低档：ref2va_pruned_int8_convrot + qwen3vl_nvfp4_awq（官方 ~24GB 级，宣称 dynamic offload 下 3060 可跑 2K）
- **官方原生模板音频干净（凡哥实测）**——⚠️ 归因纪律（凡哥纠正）：音频干净根因是 **ComfyUI 0.30.0 版本**（Director 在此版本同样干净），**不是"绕开 Director"本身**。不得把版本因素归因成组件因素。

## 官方原生模板加速与生态更新（2026-09-09 二期查证/实测）

**加速点**：官方 r2v 模板 model 链 = UNETLoader →(可插 TESpeedMiniMaxH3 → SolAttnPatch)→ BasicScheduler.model + BasicGuider.model（UNET 输出 fan-out 两节点）。TE ≈45%（本地实测）；SolAttn 稀疏窗口在 **20 步才有效**（3 步 refine 无效见上）；base 保持 20 步。

**Turbo LoRA 生态更新（旧"Turbo 仅 FL2VA"作废）**：社区 larryvrh Turbo v4 支持 T2V·I2V·FL2V·**Ref2V Mixed**；`minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` 已进官方 HF 打包（datasets 有）。ref2v turbo 用法：steps 20→**8**（作者推荐 6-8 步，不是 4），sampler 保持 res_multistep/euler + simple。诚实边界：ref2v turbo v0.1=社区预览，**参考图锁角色保真最不稳**；turbo=试镜/预览工具，终稿回 base 20 步；turbo LoRA 必须与 FL2VA/Ref2VA 家族匹配，不混用。4 步 vs 20 步 ≈采样 3.4×（端到端少些，编码/解码/加载固定开销不缩）。

**官方模板 json 格式坑**：官方下载的 API 格式 json（~7KB，class_type 图）**拖入前端不渲染**（节点为 0）；要 UI 格式（nodes/links 数组）——前端 Library 打开的是 UI 格式；本地模板包路径 `.../site-packages/comfyui_workflow_templates_json/templates/video_minimax_h3_r2v.json`。在 UI json 手工插加速节点遵守 json 铁律（links + 两端端口同步）；LoraLoaderModelOnly 插 UNET 与 sampler 之间。

**/datasets 平台公模库部署模式**：只读公模库**软链到共享盘即用**（免下载免复制）：`ln -s /datasets/ComfyUI/models/<子目录>/<文件> /home/waas/ComfyUI/models/<子目录>/` + 重启 ComfyUI 扫模型。本次软链 3 文件：ref2va_pruned_int8_convrot、qwen3vl_nvfp4_awq、ref2v_turbo_4step_v0.1。

**15s(362帧=17n+5) 2K 硬件档位（官方数据+诚实边界）**：官方无"2K×15s"专项数字；pruned INT8+NVFP4 整档 ≈24GB VRAM（官方称 12GB 靠 dynamic offload 可能跑）；社区实测 12GB 卡 FL2VA 2K 124帧 4步 turbo ≈8min（帧数是显存主因子）；ref2va pruned + 2K×15s 在 32GB = **无公开先例需实测**，建议测序 2K×8s → 1MP×15s → 2K×15s+turbo8。

**手工搭 ComfyUI json 工作流铁律**（本次踩坑）：只往 `links` 数组加线**不会画线**——必须同步更新节点端口的引用：from 节点 `outputs[i].links`（数组）append link id、to 节点 `inputs[i].link` 设 id；且节点定义若缺该口（json 只存用到的可选口），须整节点换成含完整端口的定义（如 Director 需带 refine 口/out6 的版本）。校验=遍历 links 反查两端端口引用。

## 高清成片三期结论（2026-09-09）：32GB 上 2K 的正确姿势

**放弃两条路**：① Director 2K 二采 = 32GB OOM（见上）；② 官方模板 2K 直出 = 分辨率悬崖（5090 实测 1080p=3.5h；wan2-7 实测峰值显存 ~31.8GB 全打满，pruned 不省峰值显存）。**正路 = ≤0.7MP 低清直出 + 外部放大**。社区 5090 权威数据、RTX VSR 实测与补丁、LTX2.5 跨模型放大（UP 实测主推，IC-LoRA 带参考图保脸）详见 `references/h3-2k-upscale-vsr-ltx25-2026-09.md`。

**快速要点**：
- 8s 档时间（5090）：0.3MP≈2min / 0.5MP 4m17s / **0.7MP 7m26s（最值档）** / 1.0MP 13m49s；15s(362帧) 安全档 ≈0.5MP（帧数×1.9 等效显存）。
- **RTX VSR**（Nvidia_RTX_Nodes_ComfyUI + pip nvidia-vfx）：2× 放大 11.2s/362帧；**quality 必须 HIGHBITRATE_HIGH**（原版下拉只有 LOW/MED/HIGH/ULTRA=删扩散纹理→比原糊，需一行补丁加档，见 reference）；纯超分无角色参考 → 救不回小脸/远景脸（凡哥实测质疑成立）。
- **LTX2.5 放大**（凡哥选定路线）：Spatial Upscaler 2× + IC-LoRA ingredients(0.9) 多图参考 + 音频引导 + 3步 denoise 0.25 → 去模糊保脸；5090 8s 2× 放大 3分14s、10s→1080p 3分43s 显存 25.9GB；模型 6 文件全在官方 HF 仓库（Lightricks/LTX-2.5 + Lightricks/LTX-2.3-22b-IC-LoRA-Ingredients），云上下载走 `HF_ENDPOINT=https://hf-mirror.com`。
- **纯超分/跨模型放大的共同边界（凡哥 2026-09-09 纠正）**：放大救不回"源就没拍清"的脸（无中生有=脑补=变脸）；脸要保真靠生成时脸够大（写 close-up）+ 参考图注入，不是靠放大环节。
- **★ 二采/放大前必须先处理参考图尺寸（2026-09-18 实证，UP Astral星芒 官方方案）**：`MiniMaxH3ReferenceSplitter.short_edge_max` 的 **`0` = 不缩放**（插件源码 tooltip 原文 `Short edge max pixels; 0 = no scaling.`）→ 大参考图（本例 1440×2560 / 3.7MP）**原样参与二采** → **32GB 也暴显存**，症状是 `cuMemFreeAsync` 报 `CUDA_ERROR_INVALID_VALUE` + `Fatal Python error: Aborted`（崩在 tensor 析构/释放路径，**别误判成"分配器 bug 要加启动参数"**）。
  UP 原话：「你传入的图片如果是 2K 的，参考的图片就是 2K 的，这个时候就很容易暴显存」。
  **正解**：把 `short_edge_max` 设成 **544（≈一采短边，最省）/ 816 / 1088**（`align_to` 保持 16），或喂之前先缩放参考图文件。完整因果链、被否定的自创方案、工作流作者归因法见 `references/h3-refimage-scaling-vram-crash-2026-09.md`。

## ComfyUI 内核升级 → 插件崩溃排查（2026-09-09 云 0.30→0.35 实测）

**凡哥暴怒纠正（铁律级）**：进程崩溃时**禁止在没看完整日志前断言原因**（本次连错：先猜显存边界→被小参数也崩证伪；再猜 cu128→升 cu130 仍崩）。崩溃取证与版本对应全链见 `references/comfyui-upgrade-crash-2026-09.md`，速记：

- **崩溃特征**：exit 134（SIGABRT）+ `Fatal Python error: Aborted` + 栈底 Extension modules dump = C/CUDA 层硬崩（插件与内核不兼容），不是软 OOM（软 OOM 有 Python 报错）
- **取证命令**：`awk '/got prompt/{buf=""} {buf=buf"\n"$0} END{print buf}' comfyui.log | head -60`——tail 会截掉栈顶真实异常（指向具体插件/代码行）
- **对照判据**：参数缩到已知稳档还崩 = 环境/插件问题，不是资源边界
- **0.35 内核实测**：第三方 H3 加速插件（SolAttn_triton/TE-Speed）按 0.30 内核 `minimax/model.py` 结构 monkey-patch，0.35 重构后 TE 静默失效（日志 no block_loop hooks）、**SolAttn 崩**（_forward 设 model 属性 → Fatal Abort）；triton 3.4/3.8 同点崩 = 与 triton 无关
- **官方加速正解**：0.35 内置 `--use-sage-attention`（免插件，H3 ~2×）；工作流带 SolAttnPatch 节点必须换官方原生模板
- **LTX-2.5 需 ComfyUI ≥0.32.0**（官方 Day-0）；VAE size mismatch（conv_out [48,256] vs [3,512,3,3]）= 内核太老非文件错
- **torch cu130 升级坑**：pip 不带 `-U` 不升级已装 torch → 部分升级版本错配 libcudart 崩；三件套必须 `-U` 同源（torch 2.14/torchvision 0.29/torchaudio 2.11 号体系不同，锁版先 `pip index versions`）

## 画面异常（重复人物/分屏感）排查线索

- 参考图是"同一人多视图宫格"（四格/四宫格）时，模型可能学出"画面里多个一样的人做同样的事"
- 候选解法：参考图拆单张喂 / 提示词明写"每人画面内只出现一次"
- **未验证假设，验证前不能当规则写进提示词 skill**

## 16GB 显存（本机 RTX 5080）二采上限 —— 2026-09-15 四次实测

**规律（可复用）：二采成败由「激活值规模」决定，与模型大小/显存管理策略无关。**

| 阶段 | 分辨率 | 结果 |
|---|---|---|
| 一采 | 960×544 / 15s | ✅ 三次全过，≈4.5 分钟 |
| 二采 | 1440×816（倍率 1.5） | ❌ 三次全崩：`aimdo: hostbuf_file_reader_read: device copy failed` → `CUDA error: out of memory` |
| 二采 | 1216×672（倍率 **1.25**） | ✅ **成功**，≈11.5 分钟 |

**已实测排除的两个假设（别再浪费时间）**：
1. ❌ `#1330 TiledSampler` 的 `bypass_tiling` `True→False` + `n_tiles=2` + `tile_overlap=16`：分块降的是采样器激活，**爆点在 aimdo 权重搬运**，无效。
2. ❌ 摘掉 `MiniMaxH3MemoryEfficientSageAttentionPatch`（sage 补丁）：**不是元凶**。

**有效解法**：`#1317 MinimaxH3LatentUpscaler3D` 的 `mode.scale` **1.5 → 1.25**。

**生产口径（凡哥 2026-09-15 定死）**：本机只做测试；商用必须云电脑（32GB）跑**倍率 2.0 = 1920×1088 ≥ 1080P**。全链工时：一采 4.5 分钟 + 二采 11.5 分钟 = **≈16.4 分钟/15 秒镜**。

## ⚠️ OOM 会杀死 prompt_worker → 必须重启 ComfyUI（2026-09-15 实测）

症状：`Exception in thread Thread-14 (prompt_worker)` + `torch.AcceleratorError: CUDA error: out of memory`
→ 之后新任务即便打印 `got prompt` 也**无人处理**，队列永远卡在「排队=1」（不是慢，是线程死了）。
→ **CUDA 上下文已损坏，无法热恢复 → 必须重启 ComfyUI 进程**；重启后保持 `--disable-cuda-malloc`，队列自动清空。

## ComfyUI UI 工作流 → API 提交（无头自主跑工作流）

GUI 驱动不可用（预览面板无响应 / 窗口枚举不可用）时的可行路径：
- 转换器 `D:\Hermes\cache\mv-research\ui2api2.py`：子图拍平 / **bypass 节点同类型直通重连** / 死枝剪枝 / 下拉值大小写归一化 / 手工覆盖 / 精确报错
- 提交 `submit.py`（`--nofree` 可保留节点缓存）；监控 `monitor.py`
- **三个必踩的坑**：① bypass 节点直接删会**断链**（本例 `#226 AudioLock` 的 `av_latent` 直喂一采采样器 `latent_image`），必须做同类型直通重连；② 下拉值大小写要与磁盘实际目录名一致（`MiniMax-H3\` vs `minimax-h3\`）；③ **`widgets_values` 数组才是生效值**，`widgets_values_named` 会骗人（worked 例：数组 15 / named 9，实际生效 15）

## Support Files

- `references/h3-audio-noise-case-2026-09.md` — H3 低频嗡完整案例（issue 编号、便携版部署步骤、依赖坑、**云端定制镜像整体降级失败教训**、托管平台架构与诊断探测）
- `references/waas-cloud-h3-rebuild-case-2026-09.md` — **云电脑(智算云扉)干净重建成功案例**：平台机制（数据盘/entrypoint 模板覆盖/process-compose/官方自启客服流程）、完整命令链、四坑（torchaudio cu13 崩溃、models 软链被空目录挡、工作流目录位置、开机不自启）
- `references/h3-official-r2v-template-notes-2026-09.md` — **H3 官方原生 R2V 模板云上可复用资产**：官方节点结构速查、凡哥验证的官方格式提示词模板、/datasets 公模库路径清单、Director 480P→2K 各版工作流 json 位置与实测结论（2MP refine 32GB OOM 放弃）
- `references/h3-official-r2v-native-prompts.md` — **官方原生 r2v 模板可直接粘贴的提示词样例**（8s 回家入门镜已通过音频验证 + 15s 长镜压测版 + 写作要点：单段自然语言格式、<Picture N> 引用、<d> 台词、17n+5 帧数）
- `references/h3-2k-upscale-vsr-ltx25-2026-09.md` — **高清成片三期**：社区 5090 实测数据（wan2-7 31.8GB/时间档、ai-muninn 2K 悬崖 3.5h）、RTX VSR 部署+quality 补丁、纯超分保真边界、LTX2.5 跨模型放大完整方案（6 模型清单+HF 仓库+hf-mirror 下载+UP 工作流参数）、UP 视频/转写/工作流本地位置；**第五节含 2026-09-09 落地实证**：HF gated 仓库下载实测（hf-mirror 不转发 gated、comfyicu 非 gated 镜像、Read token 流程）、UP 工作流两插件依赖（ComfyUI-LTXVideo+VHS）、IC-guide 多参考图源码接法 + 3 参考 json 交付（未实测标注）
- `references/h3-refimage-scaling-vram-crash-2026-09.md` — **H3 二采崩（`cuMemFreeAsync` CUDA_ERROR_INVALID_VALUE + `Fatal Python error: Aborted`）根因＝参考图未缩放**：`MiniMaxH3ReferenceSplitter.short_edge_max = 0`（0=不缩放）＋3.7MP 参考图硬喂 → 显存压爆；正解＝按 UP 官方把 `short_edge_max` 设 544/816/1088 或预缩放参考图（工作流作者＝**Astral星芒**）；含**被凡哥否定的自创方案**（`--disable-cuda-malloc`）与工作流作者归因法
- `references/comfyui-upgrade-crash-2026-09.md` — **0.30→0.35 内核升级崩溃排查全链**：崩溃取证命令（awk 取栈顶）、exit 134/Fatal Abort 特征判别、SolAttn/TE-Speed 第三方加速插件 vs 内核重构根因链、官方 --use-sage-attention 加速、LTX-2.5 需 ≥0.32.0 版本对应表、VAE size mismatch 非文件错判别、torch cu130 升级坑（-U 必须/三件套同源/版本号体系）、云 git tag 升级命令
- `scripts/audio_spectrum_check.py` — 音频分段频谱诊断脚本
