# ComfyUI 内核升级 → 崩溃排查全链（2026-09-09 云 0.30.0→0.35.0 实测）

背景：凡哥云端（智算云扉 RTX 5090 32GB）为跑 LTX2.5 放大把 ComfyUI 从 0.30.0 升到 0.35.0 + torch cu128→cu130。H3 一采反复崩溃（exit 134），排查链暴露三类可复用知识。

## 崩溃取证法（凡哥 2026-09-09 暴怒纠正："你为啥每次那么肯定？看日志找原因"）

**崩溃特征**：进程退出码 134（128+6 SIGABRT），`Fatal Python error: Aborted` + 栈底整段 `Extension modules: ...` dump，无 Python ERROR 日志 = C/CUDA 层硬崩（插件 kernel/API 与内核不兼容典型特征；ComfyUI 软 OOM 是能捕获的 Python 报错，不 abort）。

**取证顺序（禁止跳过）**：
1. `awk '/got prompt/{buf=""} {buf=buf"\n"$0} END{print buf}' comfyui.log | head -60` 取**最后任务完整段含栈顶**——tail -30/40 会把栈顶（真实异常与插件文件行）截掉，只剩通用栈底
2. 栈顶指向哪个插件/哪一行 → `sed -n 'X,Yp' <插件文件>` 看崩溃行代码
3. 有代码证据再下结论。**禁止在未看日志时就断言"应该是显存/版本/参数"**——本次连错三次：先猜 0.6MP 显存边界（被 0.4/0.5 也崩证伪）→ 猜 cu128 vs cu130（升 cu130 后同点崩证伪）→ 真凶是第三方插件与内核不兼容。

**对照判据**：参数缩到极小（0.4MP 8s 已知稳档）**还崩 = 不是资源边界，是环境/插件问题**。

## 真凶：第三方 H3 加速插件按旧内核 model.py 写，0.35 内核重构后崩

- TE-Speed：日志 `comfy/ldm/minimax/model.py has no block_loop hooks - run patch_model.py first. Returning the model unpatched` = 静默失效（无害）
- **SolAttn_triton：崩**。`_morton_h3.py` `_forward` 里 `model._sol_morton_active = ...`（给模型设属性）→ torch `module.__setattr__` → Fatal Abort。monkey-patch 目标（model._forward / rope_freqs / block hooks）是 0.30 内核结构，0.35 重构后 patch 点失效
- **triton 3.4 / 3.8 都崩同一位置 → 与 triton 版本无关**（判别法：换版本无变化 = 不是它）
- 结论：工作流里带 SolAttnPatch/TE-Speed 节点的旧 json，**0.35 内核下必须换官方原生模板**（Browse Templates → MiniMax H3 → Reference to Video），不能只加参数绕

## 官方加速（0.35 时代正解）

- ComfyUI 官方 Wiki（H3 指南）：**`--use-sage-attention` 启动参数 = 内置，无需自定义节点**，H3 社区报告 ~2×
- 0.35 `comfy/ldm/modules/attention.py`：SAGE_ATTENTION（sageattention 包，PyPI 1.0.6 即可）+ 可选 SAGE_ATTENTION3（`from sageattn3 import sageattn3_blackwell`，Blackwell 专用，try/except 没装就跳过）
- 启动：`python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch --use-sage-attention`

## 模型 ↔ ComfyUI 内核版本要求（版本对应表）

| 模型 | 最低 ComfyUI | 证据 |
|---|---|---|
| MiniMax H3 | 0.30.0+ | 官方 #15224（2026-08-03 day-0）|
| **LTX-2.5** | **≥0.32.0** | 官方 Day-0 博客 "Update ComfyUI to latest 0.32.0" |

**LTX-2.5 VAE size mismatch 不是文件错**：0.30 内核 VAELoader 报 `decoder.conv_out.weight: checkpoint [48,256] vs model [3,512,3,3]` → [48,256] 就是 LTX-2.5 video VAE 真身（48ch 1D conv 结构），**文件换几遍都一样 = 内核太老**，换 ≥0.32 内核解决（0.35 实测 `CausalDiffusionVAE 1403.92 MB loaded` ✓）。safetensors 验证文件真身：`safe_open(...).get_slice('decoder.conv_out.weight').get_shape()`（[48,256]=LTX video/audio-like 1D；video 3D conv 另一形态）。

## 云 git 仓库升级（浅克隆）

本地 shallow clone 只有一个 tag → 升级路径：
```bash
git ls-remote --tags origin | grep -oE "v0\.[0-9]+\.[0-9]+$" | sort -V | tail   # 查最新稳定
git fetch origin tag v0.35.0 --depth=1 && git checkout v0.35.0                  # 拉目标 tag
/home/waas/h3-0300/venv/bin/pip install -r requirements.txt                     # 补依赖（aimdo/kitchen/frontend 自动升）
```

## torch cu130 升级坑（0.30 时代 cu128 同款教训重演）

1. **`pip install torch torchaudio --index-url cu130` 不带 -U 不升级已装 torch**——只装了缺的 torchaudio 2.11.0+cu130 配旧 torch 2.8.0+cu128 → `OSError: libcudart.so.13`（与当年 cu13 版 torchaudio 配 cu12 torch 完全同款）。**必须 `pip install -U torch torchvision torchaudio --index-url <cu源>` 全家同源升级**
2. 版本号体系不同，锁版前先查实际可用：`pip index versions <pkg> --index-url <cu源>`。cu130 源（2026-09）：torch 最新 **2.14.0**、torchaudio 最新 **2.11.0**、torchvision **0.29.0**（0.x 号体系）——不能拿 torch 号去锁 torchvision
3. 装完全套：torch 2.14.0+cu130 / torchvision 0.29.0+cu130 / torchaudio 2.11.0+cu130 / triton 3.8.0（自动）/ cuda True ✓；nvidia-cudnn-cu13 等 runtime 13 全家自动带（解决 libcudart）
4. 大 wheel（~5GB nvidia 全家）**用 nohup 后台 + 日志轮询**——前台跑会一直占 shell 无输出，用户以为"没反应"；`pkill -f "pip install"` 可杀
5. 0.35 启动警告 "nvidia 20 series and above required cu130+" = 硬性要求（cu128 下 H3 采样 kernel 层崩溃）

## 遗留（2026-09-09 会话结束时未闭环）

- IC-LoRA 文件曾报 `safetensors header is too large` = 文件坏/150B 残留——`ls -la`/`head -c 200 | xxd` 验证；正确文件约 1GB 需从官方/夸克获取（hf-mirror 不转发 gated）
- 0.35 + cu130 + 官方模板 + sage 的 H3 出片（音频验证）与 LTX2.5 放大端到端**待凡哥实测**
- 多参考图 json（`LTX2.5放大视频_3参考图_云版.json`，LoadImage×N → ImageBatch 合并 → IC-guide 直连）仍为未实测交付
