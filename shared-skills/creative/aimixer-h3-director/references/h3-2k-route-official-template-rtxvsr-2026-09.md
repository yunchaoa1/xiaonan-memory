# H3 32GB 云机 2K 终局结论 + 官方原生模板 + RTX VSR 路线（2026-09-09 全套实测）

> 背景：云扉云电脑 RTX 5090 32GB / 122GB RAM / ComfyUI 0.30.0 / 共享盘 + /datasets 软链。
> 目标曾为"Director 480P 一采 → Refine h3_latent 二采到 1920×1088"，实测后**该路线在 32GB 判死**，正确路线=官方原生模板低清生成 + RTX VSR 视频超分。

## 一、为什么 Director 2K 二采在 32GB 无解（实锤链）

1. `Allocation on device` = 真 OOM（不是 shape mismatch 回退，见 refine-upscale-oom-2k-case）。日志铁证：`[WARNING] Segment 1 refine failed (Allocation on device ); keeping last successful pass.` → 输出=只 latent 放大无精修 → 比一采糊。
2. **换小模型救不了**：ref2va_int8_convrot(staged 32.4GB)+qwen int8(25.8GB) → 换 pruned int8(19.9GB)+nvfp4_awq(14.9GB) 后 **2K refine 仍 OOM** → 峰值在 2K latent 采样激活，不在模型驻留。
3. 官方 LBH upscaler README 原话：*"This saves time, not VRAM — the refinement pass still runs at the target resolution."*
4. sageattention：PyPI/tuna 镜像**最高只有 1.0.6**（无 `sageattention.core`，KJ H3 sage 补丁必败）；**2.x 只在 GitHub/源码，PyPI 不发** → 云上拿不到 → sage 链判死。
5. SolAttn 对 3 步 refine 无效：稀疏窗口 start0.2/end0.9 在 3 步里几乎覆盖不到（前 20%/后 10% 仍是 dense）。
6. 结论：**注意力补丁都不是 2K OOM 的解法**。别在"把 sage/SolAttn 装对就能 2K"上继续耗（曾误导凡哥两轮）。

## 二、5090 32GB 边界数据（社区实测，未来直接引用）

**wan2-7.io 《MiniMax H3 Requirements: 36 FL2VA Runs》**（5090/32GB/128GB RAM/0.30.0/8s=192帧）：
- **峰值 VRAM 恒 ~31.8GB（31,745-31,798 MiB），三种检查点都一样** → pruned 只省磁盘/RAM，**不省峰值显存**；32GB+128GB RAM = 最低直接支持配置。
- 8s 档：0.3MP≈2min / 0.5MP 4m17s / 0.7MP 7m26s（最值档）/ 1.0MP(1376×768) 13m49s。未测 2MP、未测 15s、未测 ref2va。

**ai-muninn.com（5090，Part 1/2/3）**：
- **2K 直出 = 分辨率悬崖**：864×480 105s → 720p 239s（近线性）→ 1920×1080 **12,599s=3.5h（120×暴涨）** → 32GB 别碰 2K 直出/2K 重绘。
- 正解实测：960×540 生成 → 超分 → 1920×1080，15s(362帧)含音频全流程 **314s**（20步+RealESRGAN 625s → 14步 507s → +SageAttention2.2 412s → +RTX VSR 314s）。
- 显存负载 ≈ 分辨率 × 帧数：8s@1MP 峰值 31.8GB 临界成功 → **15s(362帧) 只能 ≤0.5MP**（15s@1MP OOM 是正常物理边界，不是配置错）。15s@0.7MP 等效≈1.33MP×8s → 险。

## 三、官方原生模板路线（绕开 Director 的 2K 入口）

- 节点 **`MiniMaxH3ReferenceToVideo`**（ComfyUI 0.30.0 自带，本地包 `python_embeded/Lib/site-packages/comfyui_workflow_templates_json/templates/video_minimax_h3_r2v.json` 为 UI 格式）。Library → Video → "MiniMax H3：参考生视频"。
- 模型自动配 pruned 小文件：ref2va_pruned_int8_convrot + qwen3vl_nvfp4_awq（/datasets 软链后即见）。
- **⚠️ 前端渲染只认 UI 格式 json**：官方 7KB API 格式 json 拖入画布=空白（凡哥踩过）。给凡哥的交付件必须是 UI 格式（大 json 带 nodes/links）。
- 图结构（UI 23 节点实证）：`MiniMaxH3ReferenceToVideo` **没有 model 输入口**；模型链 = `UNETLoader(127) → BasicScheduler(124).model` + `BasicGuider(126).model`（扇出）；cond = 136.positive→126；latent = 136.LATENT→SamplerCustomAdvanced(125)。**TE/SolAttn 加速插点 = 127 → 新节点 → 124&126**。
- 提示词 = **自然语言单段 + `<Picture N>` 引用**（非 Director 六段）；参考图 ref_images.ref_image_0/1…多张；ResolutionSelector 设 megapixels；Duration 秒 → ComfyMathExpression 自动算 17n+5 帧（15s=362）。
- 音频干净归因（凡哥纠正）：**0.30.0 版本功劳，与官方模板/Director 无关**——Director 在 0.30.0 也干净；杂音是 0.30.2+ 的 bug。
- 成品 json（本地 D:\数字资产\云电脑工作流\，凡哥拖入即用）：
  - `video_minimax_h3_r2v_TE加速_UI版.json`（25 节点：+TESpeedMiniMaxH3+SolAttnPatch，base 20 步，质量优先）
  - `video_minimax_h3_r2v_Turbo8_云版.json`（+LoraLoaderModelOnly ref2v turbo v0.1，8 步，速度优先/试镜）
  - Turbo 版需先软链 datasets lora：`ln -s /datasets/ComfyUI/models/loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors /home/waas/ComfyUI/models/loras/`

## 四、RTX VSR 超分到 1080p（有 5090 成功案例）

- 插件 **Comfy-Org/Nvidia_RTX_Nodes_ComfyUI**（git clone → custom_nodes）+ pip **nvidia-vfx**（云已装 0.1.0.1；x86_64 only）。节点 `RTXVideoSuperResolution`。
- 质量档 **HIGHBITRATE_HIGH**（标准 LOW/MEDIUM/HIGH/ULTRA 是为有压缩伪影的素材去伪影；扩散直出无伪影 → 标准档会误删真实纹理）。
- 尺寸：960×540 生成 → 2× = 1920×1080 精确。864×480 源 → 2× = 1728×960 → ffmpeg 一步到 1920×1080。
- **540px 静默 bug**：`_empty_av_latent()` 高 //16 floor → 540→528 不报错；需在工作流里 `ImageScale(bilinear 960×540, crop=disabled)` 校正后再超分。
- 耗时：VSR 腿 11.2s/362帧（RealESRGAN x2plus 109s）；音频走原片 mux 保留（ffprobe 验证 1920×1080·24fps·362帧·stereo）。
- 其他无损快档（ai-muninn）：模板 20 步→14 步 −18.9% 无可见损失；sageattention 2.2.0 −18.8%（云拿不到 2.x，跳过）。
- 官方示例 json 在云：`/home/waas/h3-0300/ComfyUI/custom_nodes/Nvidia_RTX_Nodes_ComfyUI/example_workflows/rtx_video_upscale.json`。

## 五、/datasets 平台公模库（免下载模型源）

- 只读共享库：`/datasets/ComfyUI/models/{diffusion_models,text_encoders,loras,latent_upscale_models,...}` = **ComfyUI 单文件全量**（含 ref2va pruned/int8/bf16、fl2va pruned/int8/fp8、hybrid b15-49 系列、qwen nvfp4/bf16/int8、music3、8step/4step/lightx2v/ref2v turbo lora、3d upscaler fp16/fp32…）。
- `/datasets/studio/huggingface/models/*` = **HF 仓库原样镜像（分片原始权重，非 ComfyUI 单文件）**，不能直接用。
- 用法：软链进共享盘即可：`ln -s /datasets/ComfyUI/models/diffusion_models/<文件> /home/waas/ComfyUI/models/diffusion_models/`（软链后重启 ComfyUI 扫到）。勿 cp（占盘）。

## 六、Turbo LoRA 生态更正（2026-09-09 官方/社区查证）

- "Turbo 仅 FL2VA" **过时**：官方 H3 turbo lora（Comfy-Org 发布）确实 fl2v 系；但社区已有 **Ref2VA 可用 turbo**：datasets 里 `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16`（官方 HF 仓库也打包了它）+ minimax3.com 页面列 **larryvrh Turbo LoRA v4 支持 T2V/I2V/FL2V/Ref2V Mixed（建议 6-8 步）**。
- 诚实边界：**Ref2VA turbo 参考保真最不稳（社区 v0.1 preview）**——凡哥锁角色流程慎用终稿，适合试镜/预览；质量偏好 base 20 步（社区共识 final delivery 用 base）。
- Director 语境仍成立：一采 r2v 主生成不挂 turbo，turbo 只挂二采 refine（低步数保质量）；上面 Turbo8 版是**官方原生模板**的玩法（不同语境）。

## 七、交付偏好（凡哥 2026-09-09 多次纠正）

- 云端动作**一次给一条完整命令块**（软链+pip+重启+验证串一起），别拆多条让他分跑；交付 = 部署命令 + 工作流文件一起给，只给 json 不给部署 = "你没把模型配置到云电脑"事故。
- **例外：排查/取证据类命令要分开单条给**（凡哥 2026-09-18 原话"你分开给我"）——看日志、查显存、抓崩溃现场这类，**一条命令一件事**，每条独立可跑（路径写全、不依赖上一条的变量），方便他逐条跑、逐条把输出贴回来。**判据：部署/动作 → 一整块；取证/诊断 → 拆单条。**
- json 给 UI 格式（拖入能渲染），不给 API 格式。
- 归因要准：audio 干净=版本功劳；效果归因错误会被凡哥抓（"0.30.0 和官方工作流有什么关系？"）。
- 引用社区数据时注意域名歧义（wan2-7.io 是博客域名，内容全 H3，别让凡哥误以为查错模型）。
- 凡哥问"能加速多少"要数值依据；问"官方硬件参数/成功案例"先查官方与社区实测再答，不凭记忆拒绝（"Turbo 仅 FL2VA"曾导致给错建议）。
