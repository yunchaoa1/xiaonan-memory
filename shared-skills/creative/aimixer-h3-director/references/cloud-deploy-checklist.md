# H3 导演台云端/新机部署清单（2026-09-04 云扉部署 + 2026-09-09 云上从 0 重建干净环境 + 平台自启机制实证）

凡哥要把"可一采可二采工作流"部署到云计算机（waas.aigate.cc 智算云扉/AI Cote 容器平台）。以下为完整依赖清单，官方来源=插件仓库 README + 2026-09-09 云上实机验证。

## 0. 路线选择（2026-09-09 实测定案）

- **弃用**：平台官方「ComfyUI_v0.30.1-支持MiniMax H3」定制镜像——跑 H3 有低频杂音，且镜像深度定制（加密服务/动态下发启动脚本/大量捆绑插件），整体 git 降级 ComfyUI 会破坏插件配对直接崩溃（LTXVideo `interleaved_freqs_cis` ImportError + Fatal Abort）。
- **铁证**：v0.30.1 与 v0.30.0 后端代码逐字相同（`git diff v0.30.0 v0.30.1 -- comfy/ comfy_extras/` 为空，仅前端包 52c623cf 差异）→ 0.30.1 本身不该有杂音，旧镜像杂音根因疑在定制层，**未追**。
- **干净路线（凡哥亲验无杂音）**：平台**基础 pytorch 镜像**（pytorch 2.8.0 / CUDA 12.8 / Python 3.12 / ubuntu2204，5090 需 cu128+）上**从 0 自建** ComfyUI v0.30.0 + 5 个**锁本地验证版**插件 + 共享盘模型软链。

## 1. 前提：ComfyUI 版本

- **必须 v0.30.0+**（官方 MiniMax H3 节点 PR #15224/#15228 才进主干）。跑 H3 干净版 = **v0.30.0**（0.30.2/0.31 有低频嗡杂音 bug，官方 issue #15614；0.33.1 更糟=音频静音 #15799）。
- 云端若是旧版：先在云平台选新版/重装，否则导演台节点不识别。

## 1b. 云上从 0 重建清单（2026-09-09 验证版，见 SKILL.md 顶部"云上干净环境路线"）

实例：AI Cote 新实例 = pytorch 2.8.0+cu128/ubuntu2204 基础镜像 + 5090-32GB + HTTP 8188。目录全部放**数据盘** `/home/waas`（重启/换镜像不丢）：

```bash
# ComfyUI v0.30.0
mkdir -p /home/waas/h3-0300 && cd /home/waas/h3-0300
git clone --depth 1 --branch v0.30.0 https://github.com/Comfy-Org/ComfyUI.git ComfyUI
# venv 复用预装 torch（--system-site-packages 继承 /root/miniconda3 的 torch 2.8.0+cu128）
/root/miniconda3/bin/python -m venv --system-site-packages /home/waas/h3-0300/venv
/home/waas/h3-0300/venv/bin/pip install -r /home/waas/h3-0300/ComfyUI/requirements.txt
```

**5 插件全部锁本地验证版 commit**（`cd .../custom_nodes && git clone <url> && git -C <dir> checkout <hash>`）：

| 插件 | 仓库 | 锁 commit |
|---|---|---|
| TE-Speed-MiniMaxH3-OSS | HELPMEEADICE/TE-Speed-MiniMaxH3-OSS | `c1dacf4` |
| ComfyUI-SolAttn_triton | kijai/ComfyUI-SolAttn_triton | `0e334dc` |
| ComfyUI_MiniMaxH3_Director | AIMixer/ComfyUI_MiniMaxH3_Director | **`a148812`**（8/28 验证版，勿用新版） |
| ComfyUI-MiniMaxH3DualClockSampler | shuaixn/ComfyUI-MiniMaxH3DualClockSampler | `986f8e9` |
| ComfyUI-KJNodes | kijai/ComfyUI-KJNodes | main 最新 |

插件依赖：`cd custom_nodes && for d in */; do [ -f "$d/requirements.txt" ] && /home/waas/h3-0300/venv/bin/pip install -r "$d/requirements.txt"; done`（triton 3.4.0 base 预装，无需另装——**Linux 用官方 triton，不是 triton-windows**）。

**模型软链**（共享盘模型直接复用，不复制）：

```bash
mkdir -p /home/waas/ComfyUI/output
# ⚠️ 坑：ComfyUI 首次启动会自建空 models/ 目录挡软链（ln 报错被 2>/dev/null 吞=静默失败），先删再链
rm -rf /home/waas/h3-0300/ComfyUI/models /home/waas/h3-0300/ComfyUI/output
ln -s /home/waas/ComfyUI/models /home/waas/h3-0300/ComfyUI/models
ln -s /home/waas/ComfyUI/output /home/waas/h3-0300/ComfyUI/output
# 验证必须看到 lrwxrwxrwx ... models -> /home/waas/ComfyUI/models（带箭头=成功）
```

**启动**（无平台自启，手动拉起；日志 `/home/waas/h3-0300/comfyui.log`）：

```bash
cd /home/waas/h3-0300/ComfyUI && unset PYTHONPATH && nohup /home/waas/h3-0300/venv/bin/python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch >> /home/waas/h3-0300/comfyui.log 2>&1 &
ss -tlnp | grep 8188   # 有输出=成功
```

**启动失败坑：`OSError: libcudart.so.13`**——requirements.txt 的 torchaudio 无版本限制，pip 装成最新 2.11.0（cu13 编译，找 libcudart.so.13；torch 2.8.0+cu128 只有 so.12）→ 崩溃。修：

```bash
/home/waas/h3-0300/venv/bin/pip uninstall -y torchaudio
/home/waas/h3-0300/venv/bin/pip install torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
```

## 2. 插件（核心就 1 个）

**ComfyUI_MiniMaxH3_Director**（AIMixer 导演台）
- 仓库：`https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director.git`
- 安装方法 A（有 ComfyUI-Manager）：Manager → Custom Nodes Manager 搜 MiniMaxH3 → Install；或 Install via Git URL 填上面地址 → 重启。
- 安装方法 B（有终端）：`cd ComfyUI/custom_nodes && git clone <url> && pip install -r ComfyUI_MiniMaxH3_Director/requirements.txt` → 重启。
- 可选依赖：`scenedetect`/`opencv-python-headless`/`imageio-ffmpeg`（源视频/分割用，r2v 纯参考图不需要）；`nvidia_rtx_vsr` 非硬依赖。

### 2b. 缺失节点→插件归属速查（2026-09-07 凡哥云端截图实锤）

拖入官方二采工作流后 ComfyUI 报缺失节点，**别以为全在导演台插件里**——按此映射装（截图报的 4 个缺=2 个插件）：

| 缺失节点 | 所属插件 | Git 地址 |
|---------|---------|---------|
| `MiniMaxH3Director` / `MiniMaxH3DirectorRefine` | ComfyUI_MiniMaxH3_Director | `https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director.git` |
| `MiniMaxH3MemoryEfficientSageAttentionPatch`（×2） | **ComfyUI-KJNodes**（kijai） | `https://github.com/kijai/ComfyUI-KJNodes.git` |
| `PathchSageAttentionKJ`（同工作流内） | **ComfyUI-KJNodes**（kijai） | 同上 |

## 3. 模型文件与目录（models/ 合并到 ComfyUI/models/）

来源：HuggingFace `Comfy-Org/MiniMax-H3` 或 Comfyit 文章 506（https://comfyit.cn/article/506）整合包。

| 文件 | 目录 |
|------|------|
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors`（r2v/v2v/rv2v 用；云盘同族= `minimax_h3_ref2va_int8_convrot.safetensors`，凡哥云上验证 OK） | `models/diffusion_models/` |
| `minimax_h3_fl2va_pruned_int8_convrot.safetensors`（t2v/i2v/fl2v 用） | `models/diffusion_models/` |
| `qwen3vl_32b_minimax_h3_*.safetensors`（CLIP，官方模板写 nvfp4_awq 版；type 必须选 `minimax`；云盘=int8_convrot） | `models/text_encoders/` |
| `minimax_h3_video_vae_fp16.safetensors` | `models/vae/` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/vae/` |
| `minimax_h3_latent_upscaler_3d_bf16.safetensors`（二采 latent upscale） | `models/latent_upscale_models/` |

**latent upscaler 下载地址（2026-09-07 实查）**：此文件**不在 `Comfy-Org/MiniMax-H3` 官方仓库**（38 文件无它），在第三方镜像仓库（文件完全相同）：
- `https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/main/minimax_h3_latent_upscaler_3d_bf16.safetensors`（主选）
- 镜像：`Konteni2/Minimax_h3_latent_Upscaler`、`PixelAlchemist123/Minimax_h3_latent_Upscaler`（同路径结构）
- 同仓库还有 fp16 / fp32.pth 版；**工作流要 bf16**
- HF 直连慢/不通 → 前缀换 `https://hf-mirror.com/...`

注意：CLIP 文件名以云端实际下载文件为准（int8_convrot vs nvfp4_awq 均可，只要工作流里的文件名对上）。

## 4. 工作流文件（官方 example_workflows，部署即用）

插件自带：`<plugin>/example_workflows/`：
- `minimax_h3_director_r2v.json` = 官方**一采**（无 Refine 单采样，Queue 一次出 864×480 mp4）
- `minimax_h3_director_二采_加速.json` = **可一采可二采**（带 Refine + images_pre_refine 一采对比口）
- `minimax_h3_director_t2v/fl2v/v2v/rv2v/external_groups_*.json` = 其他任务
- 本地存档副本：`opc-sim/v2/07_h3_prompt/official_workflows/`（r2v 一采版 + 二采加速版 + 官方 README）

官方默认采样：0.4MP 16:9（864×480）、5s/124 帧@24fps（17k+5）、25 steps、res_multistep+simple、cfg 1.0、shift video 12/audio 3。

**云上 2K 二采工作流**：已拼好 `D:\数字资产\云电脑工作流\minimax_h3_director_r2v_480p_to_2k_云版.json`（15 节点：一采 r2v 480P + Refine h3_latent→1920×1088 + confirm_first_pass=true 两段式 + 一采预览第二路 SaveVideo）。结构布局/json 合并策略见 SKILL.md「json 结构实证」节。

## 5. 官方二采模板与本地差异（勿混淆）

- 官方 `二采_加速.json`：Refine mode=upscale + `h3_latent`（minimax_h3_latent_upscaler_3d_bf16）→ 画布默认 **2MP 1920×1088**。
- 本地跑法：Refine mode=upscale + lanczos + 4x-UltraSharp → **1MP 1376×768**；Turbo LoRA(fl2v_turbo_4step) + BasicScheduler(beta,3步,denoise 0.25) 只在 refine 重绘可用。
- 部署端按需求选画布，参数在 Refine 节点内改，**结构不动**。
- 1920×1088 是 32 对齐的 16:9（精确 16:9 的 1080 非 32 倍数，模型取 1088）；一采 864×480 同理（480=32×15）。

## 6. 平台自启机制实证（2026-09-09，用户侧无自助，只能客服）

**启动链**（PID1 实锤）：`docker-init -- bash -c "chpasswd && ( wget file-server entrypoint.sh | bash & ) && sleep infinity"` → 下载的是**GPU 类型分发器**（按 GPU_TYPE=nvidia 再 source 执行 `.../nvidia/entrypoint.sh`，311 行，不落盘）。

**nvidia/entrypoint.sh 每次开机必做**：从 file-server **下载覆盖 5 个文件**到 `/etc/waas-script/`：`process-compose.yml`、`restart_comfyui.sh`、`waas-welcome.sh`、`proxy.sh`、`unset_proxy.sh`（时间戳回到 6/24 模板版=被覆盖铁证）→ **改 process-compose.yml 加 ComfyUI 进程=开机被还原，无效**（已实验）。

- process-compose 托管 SSH/JupyterLab/VSCode/WebOS（`WAAS_IMAGE_VERSION=V2` 分支最后 `process-compose up -f ...`）。
- `/etc/waas-script/start.sh` 钩子 **不被 V2 entrypoint 调用**（已实验：放 start.sh + 重启，hook 标记未触发）。
- `.env`（`/etc/waas-script/.env`）会被 source 加载且**不在覆盖列表**，但只能导环境变量、不能加进程。
- **官方 ComfyUI 镜像能自启的真正原因**：镜像构建时 docker-init 入口命令直接含 `nohup bash /etc/waas-script/start.sh`（镜像级定制，实例内改不了）。
- **唯一正道**：《容器启动项目指南》→ ①start.sh 放 `/etc/waas-script/`（chmod +x）②控制台**保存镜像**（运行中实例一键存系统盘；镜像名/时间记下）③提交客服：启动脚本文件名+镜像名+保存时间，请求改该镜像容器入口命令 → 客服验证后开机自启。
- 实例生命周期：关机/开机保留系统盘+数据盘（可写层保留，但 waas-script 5 文件仍被平台覆盖）；"释放"删系统盘（数据盘 /home/waas 还在）。模型/输出/自建环境**一律放 /home/waas**。
- 参考文档：docs.aigate.cc「容器启动项目指南」bestPractice/containerStartupProjectGuide、实例镜像指南 instance-mirror/instance、mirror。

## 7. 装完自检

1. 拖入 r2v 一采工作流，CLIP Loader type 确认 `minimax`。
2. 填一组测试 prompt + 1 张参考图（input/ 下），Queue。
3. 出 `output/video/MiniMaxH3_Director_*.mp4` = 一采链路通。
4. 云上验收判据（2026-09-09）：无台词段安静无低频嗡 + 台词人声清晰（8s 单段 25 步 ≈ 6.5 分钟，qwen32B int8 首次加载慢属正常）。
