# 云端 Linux ComfyUI 升级 + LTX-2.5 放大部署全程实录（2026-09-09，RTX 5090 32GB）

智算云扉 waas 实例（/home/waas/h3-0300，venv，models 共享盘）从 ComfyUI 0.30.0 → 0.35.0 + torch cu130，为跑通 LTX-2.5 放大（UP 啦啦啦的小黄瓜方案）的实际过程。一次只变一个变量逐步验证。

## 背景与目标
- 原环境 0.30.0 跑 MiniMax H3 官方模板出片（15s 0.4MP 上限，32GB 物理边界：VRAM≈分辨率×帧数；8s 可 1.0MP≈31.8GB 打满，15s 362帧 建议 ≤0.5MP）。
- H3 480P 成片 → 高清正路 = LTX-2.5 22B + IC-LoRA(ingredients) + latent spatial upscaler x2 低降噪重绘（0.4-0.7MP 一采 → 2× → 1080p/2K）。
- 放大工作流（UP json，31 节点）：LTXVLatentUpsampler + `ltx-2.5-latent-spatial-upscaler-x2`（x2 定死，工作流无倍数旋钮）；euler_ancestral/3步/denoise0.25/CFG1；IC-LoRA 强度 0.9；audio-vae 引导保口型；提示词 `[0s-2s]` 时间格式。

## 1. 插件与文件坑
- 需装：`Lightricks/ComfyUI-LTXVideo` + `c0untFloyd/ComfyUI-VideoHelperSuite`（LTXAddVideoICLoRAGuide 不在内核，comfy_api_nodes 无此节点）。
- **kornia 0.8.x 移除 `kornia.geometry.transform.pyramid.pad`** → LTXVideo 的 pyramid_blending.py `from ...pyramid import pad` 失败 → 整个插件 IMPORT FAILED（其余插件正常加载）。
  修（不降 kornia）：python 替换 import 段，去掉 pad，文件内加 `def pad(x,p,mode="constant",value=0.0): return F.pad(x, tuple(p), mode=mode, value=value)`（F 已 import）。
- **LTX-2.5 video VAE 结构 = 无前缀 1D conv（decoder.conv_out [48,256]），audio VAE = `audio_vae.` 前缀**。0.30 内核不认识 video VAE（报 `size mismatch ... current model [3,512,3,3]`）——**不是文件坏了**，互换/换源都报错 = 内核太老（需 ≥0.32）。0.35 下 CausalDiffusionVAE 正常加载（1403MB）。
  - 教训：镜像仓库文件别急着判"放反了"；先确认内核是否支持该模型结构（0.30 连 LTX-2.5 video VAE 的 1D 结构都不支持）。
- IC-LoRA（Lightricks/LTX-2.3-22b-IC-LoRA-Ingredients，gated 1GB）hf-mirror 不转发授权（150B 错误页），只能官方浏览器/夸克/用户本地上传。上传通道：凡哥用 **FileZilla SFTP**（`root@*.region1.waas.aigate.cc:44502`）——网页终端无法传文件。

## 2. ComfyUI 0.30 → 0.35.0
- 仓库是 shallow clone（git log 显示 grafted，本地只有 v0.30.0 tag）→ `git ls-remote --tags origin` 查远端 tag → `git fetch origin tag v0.35.0 --depth=1` → checkout。
- `pip install -r requirements.txt` 自动更新 comfy-aimdo 0.5.3 / comfy-kitchen 0.2.33 / frontend 1.51.10 / workflow-templates 0.11.57。
- 全部插件（Director/TE-Speed/SolAttn/KJNodes/VHS/RTX/LTXVideo）在 0.35 加载成功（0.0-0.7s），无一 IMPORT FAILED。

## 3. torch cu130 升级（0.35 硬性要求：RTX 20 系以上）
- 0.35 启动日志原文警告 cu130 必需；cu128 下 H3 采样崩溃。
- `pip install -U torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130`（**必须 -U**：pip 默认不升级已装包 → 只升 torchaudio 会 libcudart.so.13 崩）。
- 版本号体系不同步：torch 2.14.0+cu130 / **torchvision 0.29.0+cu130（0.x 独立号）** / torchaudio 2.11.0+cu130（torchaudio 号滞后 torch）。按 torch 号猜 torchvision/torchaudio 必错（2.11.0 无对应 torchvision）；让 pip 无锁解析或先 `pip index versions <pkg> --index-url ...` 看真实可用。
- torch 2.5GB+ wheel + nvidia-* 全家（cudnn 553MB 等）→ 必须 nohup 后台 + tail 轮询；前台跑会长时间无输出占死 SSH。
- 安装结果自带 nvidia-cuda-runtime-13 → libcudart.so.13 问题顺带解决。

## 4. 0.35 内核 vs 第三方加速插件（详见 SKILL.md 主文）
- TE-Speed 静默失效（no block_loop hooks）；SolAttn_triton Fatal Aborted（_morton_h3.py → module.__setattr__）。triton 3.4 与 3.8 都崩 = 与 triton 无关，内核 minimax/model.py 重构。
- 官方加速 = `--use-sage-attention`（内置，sageattention pip 即可）。
- **aimdo 0.5.x + sage = 官方已知 OOM**（Comfy-Org/ComfyUI #16144 H3 泄漏、#15759 VRAM grow failed、#12943）。特征：`VRAM grow failed: 115691520 bytes` 时 torch 显示 VRAM Free 31GB+ → aimdo 记账 bug 非真 OOM。社区解法：去掉稀疏/sage 路径即正常。
- ComfyUI 任务中断残留 → 每任务前 `POST /free {"unload_models":true,"free_memory":true}`（平台 worker 层封装，客户无感）。

## 5. 排障流程教训（凡哥两次发火纠正）
1. **崩溃先取完整日志**：`awk '/got prompt/{b=""}{b=b"\n"$0}END{print b}' log | head`——tail 只看到栈尾，真实异常在栈顶/段首（SolAttn 崩因就是这样才看到 `_morton_h3.py`）。
2. **先搜官方/社区 issue 再断言**：aimdo+sage 是凡哥反问"社区没遇到过吗？"之后 GitHub 搜到 #16144/#15759 才实锤。凡是"升级后新报错 + 特征怪（报 OOM 但显存空）"→ 第一动作 = GitHub issues 关键词搜（`"<报错串>" + <组件/模型名>`）。
3. **别把环境/参数当第一嫌疑**：凡哥原话「你确定吗？依据是什么？」「又是你脑补出来的吧？」——分辨率/显存/版本断言前必须有实测/官方出处。
4. 一次只变一个变量：升内核、升 torch、加 sage 分步验证，避免连环归因错误。

## 状态（本会话结束时）
- 0.35.0 + torch cu130 全家已装；LTX video/audio VAE、gemma、22B 主模型、upscaler 就位。
- 阻塞：aimdo+sage 冲突待"去掉 --use-sage-attention 用纯官方模板"复测确认（#16144 方向）；IC-LoRA 正确文件（凡哥夸克下载 6 件）待从本地经 FileZilla 上传覆盖 150B 残留；之后才是 LTX 放大首跑。
