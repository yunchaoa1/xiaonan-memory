# 云端 ComfyUI 环境从零重建（智算云扉 · 2026-10-08 起）

> 触发场景：环境丢失（实例释放且镜像不含环境）/ 新账号开新实例 / 要做一个「自带环境、可分享」的镜像。
> 前置平台机制先读 `waas-cloud-storage-and-mirroring.md`（镜像=系统盘快照、公模库、共享盘）。
> **状态标注**：控制台选型、安装序列 ①②③（含 torch 全家自检：torch 2.12.1+cu130 / torchaudio 2.11.0+cu130，无错配）、插件批 1/2/3 克隆（19 个目录）、插件依赖安装（12 个带 requirements 的插件全过），均于 2026-10-08 实测成功（输出已核）；模型软链、启动、端到端起片**尚待验证**——别对外说成「已全部验证」。

## 0. 三条总原则

1. **装系统盘 `/root/h3-0300`** —— 镜像 = 系统盘快照，装在数据盘（旧 `/home/waas/h3-0300`）的教训：分享镜像后对方「什么都没有」。旧路径作废，命令统一 `/root` 前缀。
2. **版本 = ComfyUI v0.37.0** —— Qwen-Image 2.1 节点（`TextEncodeQwenImage21` / `QwenImage21Cache`）要 ≥0.37.0（引入提交 `6bfaacc6` CORE-423），H3 全链也已在此版本跑通。
3. **依赖一律官方源** `-i https://pypi.org/simple` —— 国内镜像缺新包会让**整批 install 中断**（SKILL.md「为某工作流升级」坑 1）。

## 1. 控制台创建实例（2026-10-08 实测）

| 项 | 取值 | 依据 |
|---|---|---|
| 框架行 | **pytorch 2.12.1 / py3.12 / CUDA 13.0 / ubuntu2404** | 列表里**唯一** CUDA 13（其余 12.9/12.9.1/12.8/12.6）；0.35+ H3 硬性 cu130+，cu12x 采样 kernel 层崩 |
| 规格 | 5090-32GB · 系统盘 100GB · 按需计费 | 官方建议系统盘 ≤100GB |
| 端口 | 默认 8088/8080/8888/22 → **手动「+ 添加端口」HTTP 8188** | 8188=ComfyUI；缺了服务起得来但外部访问不到 |
| 环境变量 | **保留 `WAAS_IMAGE_VERSION=V2;`** | 平台 process-compose 托管 SSH/JupyterLab/VSCode/WebOS 靠它 |

## 2. 安装序列（①②③ 已实测成功）

```bash
# ① ComfyUI v0.37.0 → 系统盘
mkdir -p /root/h3-0300 && cd /root/h3-0300 && git clone --branch v0.37.0 --depth 1 https://github.com/Comfy-Org/ComfyUI.git ComfyUI && cd ComfyUI && git describe --tags
# 期望输出: v0.37.0

# ② venv 复用镜像预装 torch（--system-site-packages，不重装几 GB）
/root/miniconda3/bin/python -m venv --system-site-packages /root/h3-0300/venv
/root/h3-0300/venv/bin/python -c "import torch; print('torch', torch.__version__, '| CUDA', torch.version.cuda, '| GPU:', torch.cuda.is_available())"
# 期望: torch 2.12.x+cu130 | CUDA 13.0 | True

# ③ 依赖（官方源！输出里出现任何 ERROR 就换源重跑整条）
/root/h3-0300/venv/bin/pip install -r /root/h3-0300/ComfyUI/requirements.txt -i https://pypi.org/simple
# 关键件验收: comfy-aimdo-0.5.5 / comfy-kitchen-0.2.35 / comfyui-frontend-package-1.52.7 都在 Successfully installed 列表里
```

> 另跑一道 torch 全家自检（防 `libcudart.so.13` 类错配）：`venv/bin/python -c "import torch, torchaudio; print(torch.__version__, torchaudio.__version__)"`，报错再按 SKILL.md 的 cu 源全家升级法处理。

## 3. 插件安装（锁版 + 分批）

**批 1 · 5 个核心——commit 锁死，勿用新版**（`a148812` 是 8/28 验证版；这套组合 = 「无杂音」基线）：

```bash
cd /root/h3-0300/ComfyUI/custom_nodes && \
git clone https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director.git && git -C ComfyUI_MiniMaxH3_Director checkout a148812 && \
git clone https://github.com/HELPMEEADICE/TE-Speed-MiniMaxH3-OSS.git && git -C TE-Speed-MiniMaxH3-OSS checkout c1dacf4 && \
git clone https://github.com/kijai/ComfyUI-SolAttn_triton.git && git -C ComfyUI-SolAttn_triton checkout 0e334dc && \
git clone https://github.com/shuaixn/ComfyUI-MiniMaxH3DualClockSampler.git && git -C ComfyUI-MiniMaxH3DualClockSampler checkout 986f8e9 && \
git clone https://github.com/kijai/ComfyUI-KJNodes.git
```
（分离头指针提示属正常；以上 5 个仓库地址本批均实测可克隆。）

**批 2 · H3 相关 4 个**：`oufeixinxinren/ComfyUI-MiniMax-ContextIR` · `LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler` · `tl2012tl/comfyUI-llama-TE` · `chflame163/ComfyUI_LayerStyle`

**批 3 · 常规 10 个**（2026-10-08 全部实测克隆成功；两处曾「地址待查」的已定位，最后两个是本次新查证的）：
`rgthree/rgthree-comfy` · `ltdrdata/ComfyUI-Manager` · `crystian/ComfyUI-Crystools` · `Kosinkadink/ComfyUI-VideoHelperSuite` · `pythongosssss/ComfyUI-Custom-Scripts` · `yolain/ComfyUI-Easy-Use` · `Lightricks/ComfyUI-LTXVideo` · `larryvrh/ComfyUI-MiniMax-H3-Turbo` · **`snicolast/ComfyUI-IndexTTS2`** · **`Comfy-Org/Nvidia_RTX_Nodes_ComfyUI`**（Comfy-Org 官方仓）
装完 `ls -d */ | wc -l` 应收 **19** 个目录（加 5+4+10，comfyui 自带 .py 文件不算）。

**老机器 20 件完整清单（重建对照表，2026-10-08 从原实例 ls 得到）**：
ComfyUI-Crystools · ComfyUI-Custom-Scripts · ComfyUI-Easy-Use · ComfyUI-IndexTTS2 · ComfyUI-KJNodes · ComfyUI-LTXVideo · ComfyUI-Manager · ComfyUI-MiniMax-ContextIR · ComfyUI-MiniMax-H3-Turbo · ComfyUI-MiniMaxH3DualClockSampler · ComfyUI-SolAttn_triton · ComfyUI_LayerStyle · ComfyUI_MiniMaxH3_Director · ComfyUI-VideoHelperSuite · Comfyui_Minimax_h3_latent_Upscaler · comfyUI-llama-TE · Nvidia_RTX_Nodes_ComfyUI · rgthree-comfy · TE-Speed-MiniMaxH3-OSS
（`websocket_image_save.py` / `example_node.py.example` 是 ComfyUI 自带文件，不算插件。）

## 4. 收尾（沿用既有配方，路径改 `/root`）

1. **插件依赖**（2026-10-08 实测：12 个插件带 requirements.txt，全部安装通过）：`cd custom_nodes && for d in */; do [ -f "$d/requirements.txt" ] && /root/h3-0300/venv/bin/pip install -r "$d/requirements.txt" -i https://pypi.org/simple; done`，再用 `scripts/scan_missing_node_imports.py` 兜底扫缺。
2. **模型**：**数据盘 `/home/waas` 在实例释放后保留**（2026-10-08 实测：新实例里旧 `ComfyUI` 共享盘模型目录 + `ComfyUI_MiniMaxH3_Director` 都在）→ 直接复用它，模型零下载、输出目录也放数据盘持久化：
   ```bash
   rm -rf /root/h3-0300/ComfyUI/models /root/h3-0300/ComfyUI/output && \
   ln -s /home/waas/ComfyUI/models /root/h3-0300/ComfyUI/models && \
   mkdir -p /home/waas/ComfyUI/output && ln -s /home/waas/ComfyUI/output /root/h3-0300/ComfyUI/output && \
   ls -l /root/h3-0300/ComfyUI/ | grep -E "models|output"
   ```
   ⚠️ ComfyUI 首启会自建空 models 目录挡软链——**先 `rm -rf` 再 `ln -s`**，链完 `ls -l` 要见箭头。**数据盘真没了才退回公模库软链**（`/datasets/ComfyUI/models/...`）。
3. **启动**：
   ```bash
   cd /root/h3-0300/ComfyUI && unset PYTHONPATH && nohup /root/h3-0300/venv/bin/python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch --disable-cuda-malloc > /root/h3-0300/comfyui.log 2>&1 &
   ```
4. **工作流**：本机 `D:\数字资产\云电脑工作流\4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json` 拖进界面（镜像带不走工作流，素材靠本机备份）。
5. **验证顺序**：先跑一次 **H3 15s 基线**（确认升级没碰坏）→ 再上新工作流。
6. 全通后 → **控制台保存镜像**（此时环境在系统盘，镜像自带环境，分享/发布才成立）。

## 5. 相关

- 平台机制与官方原文：`waas-cloud-storage-and-mirroring.md`
- ⚠️ 旧版部署清单（v0.30.0 / cu128 / 装 `/home/waas`）在 `aimixer-h3-director/references/cloud-deploy-checklist.md` —— **配方已过时**，仅保留其平台机制与踩坑参照（torchaudio 错配修法、插件依赖闭环、启动参数等）。
