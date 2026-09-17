---
name: aimixer-h3-director
description: 凡哥说"导演台""多组生成""API跑H3""OPC交接"时加载。AIMixer导演台多组组装与ComfyUI API控制（含V4全能工作流云上API化）。
version: 0.1.0-rc
metadata:
  hermes:
    category: creative
    tags: [aimixer, minimax-h3, director, comfyui, opc]
---

# AIMixer H3 导演台（执行层）

凡哥本地 **H3 专用实例=便携版 ComfyUI 0.30.0（D:\SDkecheng\ComfyUI_windows_portable，端口 18189，python_embeded 在便携根目录，启动：`cd ComfyUI_windows_portable && ./python_embeded/python.exe -s ComfyUI/main.py --port 18189`）**——它是凡哥认定的 H3 无噪音干净版，装了完整 H3 套件（Director/DualClockSampler/SolAttn_triton/TE-Speed）。主版 0.30.2（D:\SDkecheng\ComfyUI，18188）跑 H3 一采曾 6 小时零产出（batch timeout），**跑 H3 一律便携版 0.30.0，不碰主版**。提示词内容本身由 `minimax-h3-shot-prompt` 编译；本 skill 管**执行层**。

## 官方一采工作流（凡哥 2026-09-04 定：按官方方式，别自己改）

插件自带官方示例在 `ComfyUI_windows_portable/ComfyUI/custom_nodes/ComfyUI_MiniMaxH3_Director/example_workflows/`：

- **`minimax_h3_director_r2v.json`（=官方一采/单次采样工作流）**：**不接 Refine 节点**，11 节点（UNET/CLIP/VAE×2/Director/CreateVideo/SaveVideo/PreviewAny）。Queue 一次**直接出 864×480 mp4**（SaveVideo 前缀 `video/MiniMaxH3_Director_*`，落 `output/video/`）。**要"一采出视频"就发/用这个，别拿带 Refine 的工作流当一采模板**。
- `minimax_h3_director_二采_加速.json`：接 MiniMaxH3DirectorRefine + LoraLoader×2 + BasicScheduler(SIGMAS)，`images_pre_refine` 口接第二路 SaveVideo 可同时导出一采对比片——官方二采结构参照。
- 官方 README 原话："不接 Refine 节点 = 原来的单次采样"；CLIP 的 type 必须 `minimax`；画布默认 0.4MP 16:9（864×480）、25 steps、cfg 1.0、shift 12/3。
- **凡哥血泪（2026-09-04）**：一采 6 小时零产出根因=拿"带 Refine 的二采工作流"（confirm_first_pass=true）当一采模板提交——第一次 Queue 只写缓存不出视频。想要一采出 mp4 → 官方无 Refine r2v 工作流（或二采工作流直接一次 Queue 由 images_pre_refine 出一采对比片）。凡哥批评"是不是又开始瞎试了？按照官方的可以出1采的方式来"——**先查插件 example_workflows/README，官方有现成的就别自己拼参数**。
- **云端/新机部署**：插件 GitHub `AIMixer/ComfyUI_MiniMaxH3_Director`、模型 HF `Comfy-Org/MiniMax-H3`、装法（Manager Git URL / git clone）、官方文件与目录清单 → 见 `references/cloud-deploy-checklist.md`（2026-09-04 云扉部署 + 2026-09-09 云上从 0 重建干净环境 + 平台自启机制实证）。
- **云上干净环境路线（2026-09-09 凡哥亲验无杂音）**：平台官方「ComfyUI_v0.30.1-支持MiniMax H3」定制镜像跑 H3 有杂音且深度定制（加密服务/动态下发启动脚本），**弃用**；干净路线 = 平台**基础 pytorch 镜像**（2.8.0+cu128/ubuntu2204）上自建 ComfyUI **v0.30.0** + 5 个**锁本地验证版**插件 + 共享盘 `/home/waas/ComfyUI/models` 软链 → 一采音频干净。平台"自启"**用户侧无自助入口**（启动链/覆盖机制实证），只能走客服《容器启动项目指南》（保存镜像+提交 start.sh）——详见 reference。
- 官方二采模板画布默认 2MP 1920×1088，本地验证是 1MP 1376×768——部署时按需改 Refine 画布，勿混淆。

## 工作流两段式结构（MiniMax+H3+导演台全能工作流）

- **一采（主链路）**：`MiniMaxH3Director`（r2v 任务，cfg=1、20 步 res_multistep/simple、shift 视频12/音频3 官方推荐、864×480）吃 UNET(ref2va_pruned_int8_convrot) + CLIP(qwen3vl_32b int8, type=minimax) + video_vae(fp16) + audio_vae(fp32)，一次采样同时产出 AV latent（视频帧+32kHz 音频）。
- **二采（Refine 放大精修）**：`MiniMaxH3DirectorRefine`（mode=upscale、lanczos、euler、passes=1）接 4x-UltraSharp 放大 + **fl2v_turbo_4step LoRA + BasicScheduler(beta, 3步, denoise 0.25)** → 输出 1376×768。Turbo LoRA 只在 refine 重绘阶段可用（Ref2VA 主生成不支持 Turbo）。
- **输出**：Director 输出 7 路 `images/audio/fps/frame_count/source_images/report/images_pre_refine`；CreateVideo 合成、SaveVideo 存 `output/video/`。
- `confirm_first_pass=true` 时一采确认后才二采。

### json 结构实证（2026-09-09 拼"480P→2K"云上工作流）

- **Director(r2v) widgets 21 项布局**（r2v json 实证）：`0 task / 1 global prompt / 2 '采样设置' / 3 cfg / 4 seed / 5 seed_ctrl / 6 fps / 7 width / 8 height / 9 ref_max / 10 total_frames / 11 timeline_data / 12 '高级采样' / 13 steps / 14 sampler / 15 scheduler / 16 shift_video / 17 shift_audio / 18 '性能' / 19 clear_vram_between_segments / 20 export_source_images`
- **MiniMaxH3DirectorRefine 12 项 widget 源码顺序**（INPUT_TYPES 实证）：`mode / upscale_method / latent_upscale_model / sampler / passes / seed_mode / aspect_ratio / megapixels / width / height / skip_fl2v / confirm_first_pass`。example json 常只存 **11 项**（尾缺 confirm）→ 加载补默认 false；要"先一采验收再二采"须**显式补第 12 项=true**
- **陷阱：不同 example json 分组标签文字不统一**（'高级采样 Advanced' vs '高级采样'、'性能 Performance' vs '性能'、widgets 21 vs 22 项）——**别按标签字符串 assert/定位，先 dump 目标 json 按 index 实测**
- 源码 tooltip 实证：Refine `sigmas` 口 mode=refine/upscale **必须接线**；BasicScheduler 必须接**与二采相同的 MODEL**（导演台主模型或 refine_model）；`refine_model` 不接=二采自动用导演台主模型 → 甩掉 turbo LoRA 的合法依据（README：turbo 只用于 refine 重绘加速，768p lora 上 2MP 画布有风险）
- **合并策略**：改工作流时以**实测跑通的 json 为主体**（Director 参数全对），只从其他 json 抄新增节点/参数——两版 example json 的 Director 结构可能不同（steps/标签长度/分组），整体改别人的 Director 必翻车
- **云上 2K 档验证组合**（产出 `D:\数字资产\云电脑工作流\minimax_h3_director_r2v_480p_to_2k_云版.json`，15 节点）：一采 Director(r2v, 864×480, 25步 res_multistep/simple, shift12/3, cfg1, seed666 fixed, 8s=192帧=17×11+5, clear_vram=false) + Refine(upscale/h3_latent/3d_bf16/euler/passes1/inherit/16:9宽屏/2MP/1920×1088/**confirm=true**) + BasicScheduler(beta,3,0.2)；模型=云盘 ref2va_int8_convrot + qwen3vl int8 + VAE×2 + 3d_bf16 upscaler（全在 `/home/waas/ComfyUI/models`）。首次 Queue 出一采 480P 预览（images_pre_refine 口第二路 SaveVideo）+ 缓存；同 seed 再 Queue 才出 1920×1088。1920×1088 = 32 对齐的 16:9（精确 16:9 的 1080 不能被 32 整除，模型取 1088）

- **turbo 加速版（2026-09-09 交付 `minimax_h3_director_r2v_480p_to_2k_turbo_云版.json`，16 节点）**：官方 example `二采_加速.json` **本身就是官方加速方案实证**——二采精修链 = 主 UNET → `LoraLoaderModelOnly(fl2v_turbo_4step, 强度1)` → Refine.refine_model + BasicScheduler.model（BasicScheduler 接**与二采相同 MODEL**=turbo 模型）；BasicScheduler(beta, 3步, denoise 0.2) 的 **3 步是提速核心**（不是 25 步）。README/skill 依据：一采 r2v 主生成**不支持** turbo（一采保持 25 步正常）；turbo 只在 refine 重绘阶段可用；refine_model 口官方 tooltip 就写"适合挂 Turbo LoRA"。云盘 v1.1_768p lora vs example 的 v1.0——同族未对比实测，先标准版测基线再 turbo 版对比。

- **全加速版/官方「组合加速」3 层（2026-09-09 交付 `minimax_h3_director_r2v_480p_to_2k_全加速_云版.json`，20 节点/24 links）**：①KJ sage 注意力链 + ②turbo LoRA（③TE-Speed 见下）。
  - ①sage 链拓扑（对应官方 `加速版.json` / `二采_加速.json`）：一采 `UNET → PathchSageAttentionKJ → MiniMaxH3MemoryEfficientSageAttentionPatch → Director.model`；二采 `UNET → turbo Lora → PathchSageAttentionKJ → SagePatch → Refine.refine_model + BasicScheduler.model`。**两个 sage 节点都来自 KJNodes**（`MiniMaxH3MemoryEfficientSageAttentionPatch` 定义在 `comfyui-kjnodes/nodes/ltxv_nodes.py`，不是 Director 插件）；`PathchSageAttentionKJ` widgets=['auto', False]（抄 example 节点时连 inputs/outputs 一起深拷贝，勿手造端口）。
  - ⚠️ **sage 链运行时依赖 `sageattention` Python 库**——新环境没装会在执行时报 `ModuleNotFoundError: No module named 'sageattention'`（node 报错 PathchSageAttentionKJ）。修复：`venv/bin/pip install sageattention` + 重启 ComfyUI。**已实锤（2026-09-09 云上）**：pip（尤其 tuna 镜像）可能给装 **1.0.6 旧版** → KJ 报 `sageattention is not new enough version or could not determine CUDA architecture`（KJ 在 `kjnodes/nodes/ltxv_nodes.py` **模块级** `from sageattention.core import ... get_cuda_arch_versions`；1.0.6 无 `sageattention.core` → import 失败 → `_cuda_archs=None` → execute 时抛错）。**先 `pip show sageattention` 看版本，必须 2.x**（1.0.6 是旧 API 版）；装新版/查 wheel 兼容见 `references/refine-upscale-oom-2k-case-2026-09.md`。本地 Win 曾因 sage 1.0.6 缺函数转 SolAttn 同因。**云上终判（2026-09-09 实测后）：PyPI/tuna 镜像最高就 1.0.6，2.x 只在 GitHub/源码 → 云上拿不到 → sage 链在云判死**；且 SolAttn 对 3 步 refine 无效（稀疏窗 start0.2/end0.9 覆盖不了 3 步）→ **注意力补丁都不是 2K OOM 的解法，别在"装对 sage 就能 2K"上继续耗**（详见 32GB 终局结论）。
  - ③**TE-Speed**（`TESpeedMiniMaxH3`，DiT 块缓存 ≈45%，本地实测验证）：`model → TESpeedMiniMaxH3(默认 0.12/0.1/0.9/2/auto/0.75) → Director.model`，25 步一采主受益。**未叠进全加速版**——它和 sage 链都 patch model，叠加顺序官方无示例（本地验证的组合是 TE+SolAttn），要叠单独出一版测。SolAttn_triton 是 "Patch Sol-Attn"（optimized_attention_override，与 sage 二选一）。

## 二采放大异常诊断（2026-09-09 云上 2K 实测：先看日志再动参数，凡哥铁律"别瞎猜，查官方"）

**症状**：upscale 二采（1920×1088）"没看到 3 步采样进度条 / 直接出片 / 比一采还糊"。

**第一反应 = 抓日志找回退实锤**（`tail -80 .../comfyui.log`），不是猜参数。健康/异常两串日志证据：

```
正常前置：[MiniMax H3 Director ... Refine: ON (upscale, sigmas euler 3-step, 二采模型, → 1920×1088, 3d_bf16)]
         [Director H3 latent upscale: 864×480 → 1920×1088 / latent 54x30 → 120x68 (scale=2.27)]  ← h3_latent 放大成功
         [Director refine pass 1/1 (sigmas wired euler 3-step, custom model)]  ← 二采真的开跑
💥失败串：[WARNING] Segment 1 refine failed (Allocation on device); keeping last successful pass.  ← 显存 OOM 回退！
         或：Segment 1 refine failed (shape mismatch ... [1032,96] vs [1508,96]); keeping first-pass latent.  ← 版本 bug 回退
         大量 aimdo VBAR "ABOVE watermark" 警告 = 显存管理极限挣扎（OOM 前兆）
```

**回退 = keeping (first/last successful) pass → 输出只有 latent 放大无精修 → 比一采糊**。两种回退根因处理不同：

1. **`Allocation on device`（VRAM OOM，2026-09-09 云上实锤）**：32GB 卡一采 25 步已把显存打满（int8 模型 staged ~32.4GB + qwen TE ~25.8GB，靠 dynamic VRAM 卸载勉强过），二采 2MP 大 latent + 重载模型 → 分配失败。**官方 example 挂 `MiniMaxH3MemoryEfficientSageAttentionPatch`（名字就叫 Memory Efficient）就是为省显存让 2K 塞进 32GB 设计的**——去掉 sage 链裸奔二采 = OOM。官方警告原文（日志）：*"Refine sigma pass is short. A custom refine_model without Turbo can look like noise. Unwire refine_model so the first-pass UNET (Turbo+Sage) is reused, or use a matching second-pass UNET."* → 正路：先把 sageattention 装对（2.x，见上节）→ 用**全加速版**（一采模型带 Turbo+Sage，二采复用省显存）。其他缓解：降 Refine 画布档位（1.5MP=1664×928 / 1.2MP=1504×832，官方分辨率表 MarkdownNote 都有 32 对齐值）、缩段长。
2. **`shape mismatch`（官方已知 bug，issue #96/#122 均 Open）**：#96（R2V 正常、**I2V/FL2V 带首帧 keyframe** 触发）——upscale 后 conditioning 未按目标画布重建（一采 token 1032 vs 二采 1508），作者建议修 `run_minimax_conditioning` 按 target 重跑；#122（9/5）竖构图也复现。→ 更新插件到官方 main（9/5+）再测；R2V 若在 a148812 遇此 → 大概率 a148812 代际缺陷，同样走更新主线（需凡哥拍板离开锁版）。

**别犯的错**：①症状是"模糊+没进度"却去调 steps/denoise/换 turbo（参数官方 example 就是 3 步 0.2 + 2MP，官网能出片——先查官方 example json 佐证参数没问题再怀疑执行）；②忽略日志中间的回退警告只盯着最终报错。

详见 `references/refine-upscale-oom-2k-case-2026-09.md`（日志全文证据、官方 issue 原文、决策链）。

## 32GB 云机 2K 终局结论（2026-09-09 全套实测后定论）：放弃 2K 二采/直出 → 官方原生模板低清生成 + RTX VSR 超分

1. **Director 2K(h3_latent) 二采在 32GB 判死**：换 pruned+nvfp4 小模型（staged 32.4→19.9GB）仍 `Allocation on device` → 峰值在 2K latent 采样激活；LBH 官方 upscaler README 明说 "saves time, not VRAM"。
2. **2K 直出也是悬崖**：ai-muninn 5090 实测 1080p = 12,599s（3.5h，720p 是近线性，过 720p 非线性暴涨）→ 32GB 别碰。
3. **5090 显存规律**：峰值 VRAM 恒 ~31.8GB（pruned 只省 RAM 不省峰值，wan2-7 36 次实测）；显存负载 ∝ 分辨率×帧数；**8s@1MP 是临界上限、15s(362帧) 只能 ≤0.5MP、0.7MP 最优档**；15s@1MP OOM = 正常物理边界非配置错。
4. **正确高清路线（有 5090 成功案例）**：官方原生模板 `MiniMaxH3ReferenceToVideo`（绕开 Director，0.30.0 自带）低清生成 → **RTX Video Super Resolution**（`Nvidia_RTX_Nodes_ComfyUI` + pip nvidia-vfx，质量档 HIGHBITRATE_HIGH，960×540 生成→2×=1920×1080；15s 镜含音频 ≈314s，ai-muninn 实证）。音频干净归因 = **0.30.0 版本功劳，与官方模板/Director 无关**（凡哥纠正）。
5. 交付物、官方模板 json 结构、插点、/datasets 公模库软链、Turbo 生态更正 → **`references/h3-2k-route-official-template-rtxvsr-2026-09.md`**。

### ComfyUI json 程序化改造铁律（2026-09-09 凡哥抓 bug：拖入后"没连线"）

1. **只往 `links` 数组加线 = 加载不显示连线**！前端按**节点 `inputs`/`outputs` 里的 link 引用**画线，必须双向同步：输出口 `links:[id,...]`（数组）、输入口 `link:<id>`（单值）。缺任一端端口引用 → 线丢。
2. **json 只保存"有连线的端口"**：官方无 Refine r2v json 的 Director 节点**没有 refine 输入口、没有 images_pre_refine 输出口**（不接 Refine 时前端不存这些口）——给该节点加 refine 链必失败。正解：**换成"带完整端口的 Director 节点"**（从接好 Refine 的 example 二采 json 深拷贝整节点替换，保留其全部 inputs/outputs），再按 index 重映射原连线 link id 与 widgets 参数。
3. **新增节点/连线用大号 id**（101+）避开原 1-N；`last_node_id`/`last_link_id` 同步更新。
4. **自检必须校验双向引用**（生成后从磁盘重读再查）：每条 link `[lid,frm,fs,to,ts]` → from 节点 `outputs[fs].links` 含 lid 且 to 节点 `inputs[真实slot].link==lid`。⚠️ 手工 addlink 到 refine 口常传 ts=None → 动态找 `name=='refine'` 的 index；**别把到 Director 的所有线都当 refine 口查**（model/clip/vae 的 ts=0/3/1/2 是真实口，照 ts 查，否则 4 条误报）。
5. **交付验收 = 凡哥拖进 ComfyUI 亲眼看线**（0 悬空 0 未同步才交付；凡哥抓过这类 bug，交付前自检到"加载即可用"）。

## timeline_data 多组组装

导演台节点 inputs 里 `timeline_data` 是 JSON 字符串。r2v 多组关键字段：

- `segments[]`：每组 `{id, start, length, frameCount, durationSec, prompt, negativePrompt, taskType, refs[], refAudios[], refVideos[], genImage, continuityFromPrev, refImageSize}`——start 为累计帧偏移，length=frameCount。
- `global.prompt`（公共提示词）+ `global.refs[]`（公共参考图，`{index, imageFile, imageB64}`）。
- `shots`/`keyframes` 是 fl2v 任务残留数据，r2v 忽略，不必清理。
- **帧数铁律：每组 frameCount 必须符合 17k+5**（H3 attention 结构约束）。snap 公式：`k = round((frames-5)/17); frames = 17*k+5`。例：345、294、243、209。
- **Picture 编号 = slot index + 1**（全局编号）：公共图 index 0-2 → `<Picture 1-3>`；每组组内 refs 挂自己的故事板用 `index: 3`（每组都是 `<Picture 4>`，因为 `merge_indexed_refs(common, segment)` 按 slot index 合并、组内优先，每组执行时只看到 3 公共 + 本组 1 张）。
- 各组提示词里故事板引用统一写 `<Picture 4>`（不是 4/5/6/7 逐个编号）；公共提示词里 `<Picture 4>` 只给一个通用定义（"本段的分镜故事板锚点：宫格按从左到右、从上到下时间顺序…"）。

## ComfyUI API 直接控制

> ⚠️ **H3 一律走便携版 0.30.0 实例：`http://127.0.0.1:18189`**（顶部凡哥铁律）。主版 18188 的 Director 虽也能注册路由，但跑 H3 一采曾 6 小时零产出（batch timeout）且是凡哥认定的非干净版——**提交 H3 任务前先确认目标端口是 18189**（curl system_stats 看 comfyui_version=0.30.0），别默认 18188。

- **提交**：`POST http://127.0.0.1:18189/prompt`，body **必须** `{"prompt": <api格式工作流>, "client_id": "任意串"}`——直接 POST 工作流 JSON 会返回 `no_prompt`。
- **API 格式**：顶层 key 是节点 ID（"1"/"12"/...），每节点 `{inputs, class_type, _meta}`。UI 格式（nodes/links）不能直接提交。
- **轮询**：`GET http://127.0.0.1:18189/history/{prompt_id}`，完成后 `outputs` 里拿文件路径；`GET /queue` 看队列。
- **图片引用**：导演台 refs 里 `imageFile` 用 `ComfyUI/input/` 下的文件名——生成故事板后**先 cp 到 input/** 再提交。
- **一采/二采切换走 `confirm_first_pass` 开关（MiniMaxH3DirectorRefine 节点内）**，但它只属于**带 Refine 的二采工作流**（凡哥原件两段式）：
  - `confirm_first_pass=true`：第一次 Queue 只跑一采，帧+音频写入缓存 `output/minimax_seg_cache/<node_id>/`（`seg_XXXX.pre.pt` + `.av.pt`/`.audio.pt`/`handoff.json`）；**此时不出 mp4**（SaveVideo 的 images 被阻断）。确认后**同 seed 二次 Queue** → 命中缓存只跑二采 → 出 1376×768 最终 mp4。
  - `confirm_first_pass=false`：一采完立刻 refine 直出二采。
  - **凡哥 2026-09-04 纠正**：这套是"先缓存验收、再二采"流程；凡哥要的**"一采就出视频"=官方无 Refine 单采样 r2v 工作流（见上节）**，不要拿 confirm_first_pass=true 当"一采出视频"方式（那只会得到缓存零视频）。
  - seed 必须 fixed（666）；二次 Queue 前不得改 seed/一采参数，否则缓存 miss 全量重跑（30+ 分钟）。
- 提交前探测：`curl http://127.0.0.1:18189/system_stats`（H3 便携版实例端口 18189；非默认 8188，也非主版 18188）。

## V4 全能工作流 API 交接（2026-09-10 云上 OPC 集成，详见 `references/v4-opc-api-handoff-2026-09.md`）

云上「V4 全能生视频工作流」（UnifiedToVideo 链，非导演台）要把出片能力交接给 OPC：OPC→agent（小何写）→ComfyUI API→出片。规格：单一直出 1920×1088、5~15s、提示词唯一入口 `221.string_1`、保留本地 Qwen 优化（凡哥拍板）。

- **链路**：`220 素材面板`→`221 ReferenceSplitter`（9图/3视频/3音频/string_1~3/size1、size2/duration）→`201 UnifiedToVideo`（prompt←`1301 Any Switch`：Qwen 优先、string_1 兜底）→一采→`1317 LatentUpscaler3D`→`1330 TiledSampler`→`245 输出`。`1297` 是子图（"模型加载"，13 内部节点，API 需铺平）。
- **⚠️ 双参数存储铁律**：新版 ComfyUI 节点 widget 值存两份——`widgets_values`(数组)+`widgets_values_named`(dict，点号 key 如 `mode.scale`)。**手改 JSON 必须两处同改**（只改数组=无效）；named 的 key ≈ API inputs key。
- **⚠️ size2 悬空坑（UP 原版即如此）**：`221.size2`(1920×1088) 标准版就没接线（`outputs[].links==[]`）；**实际二采尺寸=一采×`1317.scale`**（标准 1.5→1440×832 实测）。要 1920×1088 须 `scale=2.0`（凡哥已批，=交付版第 2 处偏离标准版）。判定悬空看 `outputs[].links` 是否空数组。
- **UI→API 转换必走官方**：界面「工作流→导出(API)」；禁手写转换器（subgraph 铺平/动态口点号 key/bypass 消解只有官方导出准）。subgraph 识别：节点 `type` 是 UUID 且 `definitions.subgraphs` 有同名 id。
- **官方素材上限（接口层硬约束）**：图≤9、视频≤3(各2-15s总≤15s)、音频≤3(各2-15s总≤15s且不能单独)、合计≤12 文件。`ref_images` 是 AUTOGROW 节点不卡数 → 约束做在接口层。duration(FLOAT 秒)自动换算 `max(5,round(dur*fps))` snap 17k+5（5s→124帧、15s→362帧）。
- **给凡哥指路报节点类型名、不报数字 ID**（同类唯一，Ctrl+F 搜类型名）；要看 ID：设置→搜 `ID`→Node ID Badge Mode→Show all。
- 节点权威定义查 `/object_info/<NodeName>`（比翻源码准）；改工作流前先 diff 标准版 `D:\Hermes\attachments\4-MiniMaxh-H3-全能生视频工作流-V4-2.json`。
- **凡哥偏好：小改参数他自己在界面改**（2026-09-10 原话"我手动改一下就可以了"）→ 报改动点时给**界面操作路径**（Ctrl+F 搜什么、双击哪个数字），不要执着于生成新 JSON 文件让他导入；生成新文件只适合结构性/批量改动。
- **测试授权边界（2026-09-10）**：凡哥要"材料"时（参考图/提示词/交接包），不要自发起测试——不主动打通云端连接、不要求他装公钥/贴凭据、不代跑出片（"谁让你自己测试了？我跟你说的？"）。跑片由凡哥发起或他明确指派；交完材料即止。
- **交付材料形态 + 直出 15s 单条提示词**（参考图+提示词两件套、去故事板版删除清单、聊天直发正文、4 切点时间表）→ `references/h3-opc-delivery-materials-2026-09.md`。

## 资源纪律（凡哥血泪，2026-09-02）

- **段间清理 `clear_vram_between_segments` 切记不要打开**（凡哥铁令）。它只清显存+卸载模型（`gc.collect` + `unload_all_models` + `soft_empty_cache`），对 RAM 爆帮助小、段间重载模型更慢。
- **每次提交任务前查 `/system_stats`**（ram_free / vram_free）。若模型未卸载（vram_free 明显低于总量），先 `POST /free` body `{"unload_models": true, "free_memory": true}` 释放腾空再操作——这正是 ComfyUI-Manager "Free model and node cache" 按钮的底层调用。
- 多段连跑（4 段 955 帧）时缓存累积曾把 32GB RAM 打到 0.1GB 剩余、走磁盘 swap 速度暴跌（单段正常、多段连跑必查内存）。
- 工作流文件（凡哥交付的 API 格式 JSON）只授权**换 prompt 内容**（timeline_data 的 global.prompt/segments prompt）；任何"为实现某个流程而改结构/开关/输出口"的冲动，先停手查作者 tooltip 或问凡哥。


- r2v 音频模式：`generate`（默认，AV latent 解码生成声音，AudioVAE 32kHz）/ `source`（参考音频原样 mux，自动归一化 44.1kHz 立体声）/ `mute`（跳过音频解码）。
- 无参考音频时（refAudios=[]）走 generate，环境声由模型生成。
- **杂音根因（实测基线修正 2026-09-02）**：
  1. **提示词被 AI 翻译工具机翻破坏**（多参长文本版确认）：字段名（`detailed_description:`→"详细描述："）、标签（`<Subject 2>`→`<科目2>`）、保留标记被翻译后音频条件引导失效→杂音，身份标签同时错乱。**导演台 UI 里粘贴提示词后禁止任何翻译/增强操作**；Queue 前抽查组提示词英文骨架（字段名/标签/时间戳/标记/`[reference generation]` 前缀）。
  2. **凡哥实测基线：单段 14s 干净提示词 = 音频正常**（剧情问题≠音频问题）。4 段 955 帧长版出现低频嗡杂音（频谱实测 93% 能量 <500Hz、主峰 100-200Hz；人声段正常 5kHz 主峰）。长版低频嗡机制**未最终确认**：待验证方向 = H3 双时钟（video shift 12 / audio shift 3）用 stock 单时钟 sampler（res_multistep）调度导致音频失配——凡哥已装 `ComfyUI-MiniMaxH3DualClockSampler` 插件但工作流未启用。**未实测前不得写成结论**。
- 排查方法（mp4 音轨噪声类型定位）：ffmpeg 提 PCM → numpy 频段能量/主峰/接缝 RMS 分析，区分白噪/接缝爆音/低频嗡——详见 `references/audio-noise-analysis.md`。
- 图片参考（global refs 齐全）但提示词被破坏时：视频尚可、音频先烂——这是判据。

## 关键参数速查

| 项 | 值 |
|----|----|
| 采样 | res_multistep + simple，20 步 |
| shift | video 12 / audio 3（官方推荐，勿乱改） |
| cfg | 1 |
| 帧率/分辨率 | 24fps / 864×480（一采）→ 1376×768（二采） |
| 参考图尺寸 | ref_max_size 864 |

## 导演台 UI 版本敏感（插件 2026-09 初大更新）

凡哥的界面疑问（2026-09-09：问新出现的 `FL2VA simple prompt` 区域、性能面板开关）常因插件版本差。**排查顺序：本地插件源码 grep 字符串判新旧 → GitHub commits 看更新主线 → 云电脑实例 grep 实际版本源码实锤**，别凭截图猜（vision 对深色小字 UI 截图不可靠）。

- 官方 commits 主线（GitHub `AIMixer/ComfyUI_MiniMaxH3_Director`）：
  - **2026-09-04 feat: 混合模式，同一时间轴每段自选 t2v/i2v/fl2v/r2v** → 新版 UI 顶部 Model Mode 下拉（T2VA/I2VA/FL2VA/L2VA/REF2VA）+ Prompt Mode（简易/Structured）；旧版教程/旧截图 UI 与新版不一致
  - 09-06 段间引导增强（引导+重绘与重绘幅度）；09-01 导演包导入导出 *.mmxpack.zip；09-02~09-07 多项交互修复
- **本地 a148812（08-28）web/ 无 "FL2VA simple prompt" 字样** → 该提示词区为 08-28 后新增
- 新版简易模式模板：`FL2VA simple prompt` 区首行 = 参考图对齐说明（Picture 1 对齐 0.00s、Picture 2 对齐片尾，**必须保留**）；FL2VA/fl2v 路径字段为 integrated_multimodal_description（**非** detailed_description），REF2VA/r2v 路径才用六段式。⚠️ 字段名细节待源码 grep 实锤，实锤前勿当定论写死
- 性能面板"按词/按段清理缓存"开关默认 false = 保持关，与"段间清理 clear_vram_between_segments 不开"铁律一致

**交付提示词按导演台 UI 两输入区分拆（凡哥 2026-09-09 纠正——别把六段一股脑塞一处）**：
- 公共参数区（公共提示词 / global.prompt）= subject_definitions + summary + retention_analysis（角色锁定/全局摘要）
- 素材组 1..N 区（组 prompt / segments prompt）= detailed_description + overall_soundscape + non_diegetic_music（当镜正文）
- 简易模板 UI 字段名与六段不同时，填内容不带字段名标签头，按 UI 现成字段行放

## 一采"零产出"诊断（2026-09-04 实战）

一采阶段产物是**帧缓存+音频缓存**（`seg_XXXX.pre.pt`/`.pt`/`.av.pt`/`.audio.pt`/`.meta.json`/`.handoff.json`），**不是 mp4**——凡哥问"一个视频也没出来"时先诊断，别急着改 skill。诊断顺序：

1. runner 日志（执行器脚本自己的 run_log.txt / firstpass_progress.json）——看批次提交记录。
2. `GET /queue`（空+历史有=已完成）+ `GET /history/{prompt_id}` 的 `status.status_str`（success=该批完成）。
3. 缓存目录 `output/minimax_seg_cache/<node_id>/` ls——**seg_XXXX 全套（pre.pt/pt/av.pt/audio.pt/meta/handoff）= 该段一采完成**。注意缓存是**每批位置性**（seg_0000..N 每批覆盖），每批跑完必须立即归档到 `firstpass_cache/batchN/<sid>/`，否则下一批覆盖上一批。
4. 单段耗时实测 ~10-12 分钟（864×480, TE-Speed+SolAttn 在位）；29 段全跑 ≈ 3-4 小时。
5. `POST /free` 偶发返回 -1（http 层异常）但 system_stats 正常——不致命，继续跑。

**子代理接管模式**：flash 子代理编译 prompt+组装 payload 可能打满 100 步（编译阶段就耗尽）——它会把执行器脚本（run_first_pass.py）写好但没跑。主会话接手：验证 payload 构建（`python build_payloads.py` 看 batches）+ 后台跑执行器（`python run_first_pass.py`）。长执行（>30 分钟）永远交给后台进程+notify，不放子代理轮询。

## Pitfalls

1. 帧数不是 17k+5 → H3 报错。多组时长先按秒数定、再 snap 帧数。
2. 提示词被机翻（见上）——交付用户填写后、Queue 前必须抽查组提示词英文骨架。
3. 组提示词漏写 `<Picture 4>` 引用 → 故事板挂上但模型不锚定（S09 曾踩）。
4. 公共提示词里给每组故事板各写一个 `<Picture N>` 定义 → 多组同 slot 时产生冲突重复定义；只写一个通用 `<Picture 4>`。
5. cache/images 里的参考图会被清理，生成故事板后立即 cp 到 ComfyUI/input/（场景四宫格曾丢失导致 image_generate 报 io_error）。
6. 多段 r2v 组间**零画面上下文**（报告："Segment continuity: OFF — r2v/v2v/rv2v use stock ReferenceToVideo"）：每组提示词必须**自包含**（开头直接写该组起始画面状态：人物位置/道具状态/姿势），**禁止"XX之后""承接上段"式跨段承接词**（曾致"递了两次纸巾"——下组把上组尾动作重演）；跨组连续动作（递纸巾）必须在一组内闭环（详见 minimax-h3-shot-prompt 的 Self-Contained Group Prompts 规则）。
7. 工作流结构/节点/开关一律不动（凡哥只授权换 prompt 内容）；想切换流程（如只跑一采）走 confirm_first_pass 开关，不靠改图。
8. **Director 警告 `gen segment #N task=r2v has no reference media — will behave like t2v/t2i` = 段执行时 timeline 里没读到参考图引用**——即使 Director UI 里"看得到图"也可能发生（图只挂在 UI 展示层/公共参数未启用 commonEnabled=false/图没写进段或公共 refs）。r2v 参考图必须落在**公共参数 refs（commonEnabled=true）或素材组内 refs** 至少一处，否则人物锁不定、按 t2v 跑。诊断顺序：先查公共参数启用开关 → 把图直接拖进要跑的素材组卡片图位（组级引用最稳）→ 上传后切走再切回确认图还在 → 重跑看日志警告消没消。⚠️ 2026-09-09 全加速版首测遇此（凡哥 UI 传图仍警告），正解仍在 UI 实测确认中——未闭环前先按上法排查，别写死结论。
