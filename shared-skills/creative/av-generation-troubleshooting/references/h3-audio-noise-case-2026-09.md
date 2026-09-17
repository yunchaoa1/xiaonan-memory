# H3 音频低频嗡案例（2026-09-03 实锤 + 2026-09-09 云端重大修正）

## 现象（本地 2026-09-03 实锤）

- 4 段 r2v 连拍（955 帧 ≈40s）视频"从头到尾低频嗡杂音"，同一提示词单段 14s 正常
- 频谱实测（numpy FFT）：93% 能量 <500Hz，全程主峰 100-200Hz，人声区（0.5-6kHz）仅 6.5%；有人声段（"妈。对不起。"）主峰跳到 5kHz 说明人声本身正常
- 排除项：不是白噪声（高频占比低）、不是接缝爆音（段边界平滑）、不是提示词翻译（干净提示词也嗡）

## 根因：ComfyUI 版本 bug（与提示词/工作流/模型无关）

GitHub 官方 issues 证据链：

| 编号 | 内容 | 状态 |
|------|------|------|
| Comfy-Org/ComfyUI **#15614** | "MiniMax H3-audio always has static and popping sounds"——报告者试遍版本/加速 LoRA/官方工作流/8-20 步/两种采样器/pruned+INT8 模型/CUDA 13.3+12.8/Sage 开关，全无效；多人 me too。**收尾：便携版 0.30.0 解决** | open |
| **#15799** | VAEDecodeAudio 恒定 DC 值（-1.0）或纯静音，视频完全正常；报告者环境 **0.33.1** 且列明 0.33.1 已含的多个修复 PR 都无效；同一权重在 Pinokio 装的其他 runner 音频正常 → 问题锁死在 ComfyUI 音频路径 | open |
| **#15972** | 修复 H3 audio VAE 被通用 center-crop 误处理（吃开头 PCM 样本）的 PR | 未合并 |
| **#15371** | 修复 H3 audio VAE DynamicVRAM 权重流式抖动（Windows/NVIDIA 复现）的 PR | 未合并 |
| kijai/ComfyUI-KJNodes **#736/#746** | sageattention 新版 wheel（2.2.0 torch custom ops）与 patch 节点兼容性问题 | open |

**版本区间精确定位（2026-09-09 git diff 实锤，修正早前"0.30.1 也嗡"的推测）**：
- 本地双版本对照实锤：0.30.2 低频嗡、0.30.0 干净
- `git diff v0.30.0 v0.30.1 -- comfy/ comfy_extras/` = **空**；`git log v0.30.0..v0.30.1` 仅 2 个提交（bump comfyui-frontend-package + 打 tag）→ **0.30.1 与 0.30.0 后端代码零差异，音频同样干净**
- 结论：嗡声 bug 的边界 = **0.30.2/0.31+**；干净版 = **0.30.0 与 0.30.1**
- **官方最新 0.33.x 仍未修复**（#15799）→ 别用最新主线跑 H3 音频；社区唯一验证干净的阵营就是 0.30.x

**推论教训**：听感"杂音一样"只是推测，版本结论必须靠 git diff/频谱对照实锤（本次差点基于错误假设在云端白折腾一圈）。

## 便携版 0.30.0 部署步骤（Windows/本地，专跑 H3，唯一已验证修复路线）

1. **下载**：GitHub `Comfy-Org/ComfyUI` releases → `v0.30.0` → `ComfyUI_windows_portable_nvidia.7z`（RTX 50 系 Blackwell 必须普通 nvidia 版=cu128+；cu126 版不支持）
2. **解压坑**：py7zr 不支持官方 7z 的 BCJ2 filter（`UnsupportedCompressionMethodError`）→ 下载官方 `7zr.exe`（https://www.7-zip.org/a/7zr.exe，602KB）执行 `7zr x 文件.7z -o目标目录 -y`
3. **模型共享**：便携版 `ComfyUI/extra_model_paths.yaml`：
   ```yaml
   comfyui:
       base_path: D:\SDkecheng\ComfyUI\models
       checkpoints: checkpoints
       clip: clip
       clip_vision: clip_vision
       configs: configs
       controlnet: controlnet
       diffusion_models: diffusion_models
       loras: loras
       upscale_models: upscale_models
       vae: vae
   ```
   验证：`/object_info/UNETLoader|CLIPLoader|VAELoader` 的模型列表可见
4. **插件复制**（custom_nodes 不共享，直接 cp 目录；**必须用与 0.30.0 配套验证过的插件版本，勿随手升最新**）：TE-Speed-MiniMaxH3-OSS、ComfyUI-SolAttn_triton、ComfyUI_MiniMaxH3_Director、ComfyUI-MiniMaxH3DualClockSampler、comfyui-kjnodes
5. **依赖**（便携版 python_embeded 是 Python 3.13，注意 cp313）：
   ```bash
   ./python_embeded/python.exe -m pip install "triton-windows==3.7.1.post27" "opencv-python-headless>=4.8" "imageio-ffmpeg>=0.4" "scenedetect>=0.6.4,<0.8"
   ```
   - **sageattention 兜底**：PyPI 只有 1.0.6（太老），GitHub wheel 源见 comfyui-update skill；最快方案=**从现有环境直接复制包**（`cp -r <旧venv>/Lib/site-packages/sageattention* python_embeded/Lib/site-packages/`——abi3 wheel 的 .pyd 跨 Python 小版本兼容，复制后 `import sageattention` 即生效）。缺它时 kjnodes `MiniMaxH3MemoryEfficientSageAttentionPatch` 节点报 "sageattention is not new enough version or could not determine CUDA architecture"
6. **启动**：`unset PYTHONPATH && ./python_embeded/python.exe -s ComfyUI/main.py --port 18189 --disable-auto-launch`（独立端口；unset PYTHONPATH 防串 Hermes venv）
7. **就绪验证**：`/system_stats` 版本=0.30.0 + 启动日志 5 插件加载 0 报错 + GPU 识别

## 分段一采导出（测试只看一采的开关）

导演台 timeline `output.exportMode`：默认 `"all"`（只出合并最终视频）→ 改 `"segments"` 后逐段导出 `output/minimax_seg_export/<时间戳>/seg_XXXX_pre.mp4`（一采 480P 带音频，可直接判杂音/内容）。

`confirm_first_pass=True` 机制：第一次 Queue 只跑一采（缓存到 `output/minimax_seg_cache/<node_id>/`，不落 mp4）；同 seed 二次 Queue 命中缓存只跑二采才出最终 mp4。**测试阶段只跑一采**（凡哥 2026-09-03 纪律）。

## 频谱判读细节

- 嗡声判据：**无台词段**也有 60%+ 能量 <500Hz 且人声区≈0
- 台词段低频占比高是正常：女声基频 165-255Hz、男声 85-180Hz
- 每 5 秒窗口主峰跟踪可定位"哪段时间正常（人声/水声主峰在 0.5-5kHz）哪段时间嗡"

## 云端托管实例（智算云扉 waas.aigate.cc / AI Cote，2026-09-09）

### 平台形态
- Linux 无桌面托管：无黑框，ComfyUI 经平台"服务端口 comfyui"→ Web 8188；系统工具 = SSH / 云扉OS / JupyterLab；GPU RTX 5090-32GB
- 镜像名如 `Comfyui_v0.30.1-支持MiniMax H3`：自带 ComfyUI + 大量预装插件 + 深度定制层（file-server 动态 entrypoint、proxy.sh、加密服务 main1.py、aigate-comfyui-app）

### 平台架构（start.sh 源码实锤）
- `/home/<user>/ComfyUI` = SOURCE_BASE（**共享盘/持久数据**）：start.sh 把其 `models`、`output` 软链到镜像层代码目录
- `/root/comfyui/ComfyUI` = TARGET_BASE（**镜像层代码**，完整 git 仓库带 tag）→ 整实例重启后代码改动可能被镜像快照还原，重启后必须复核
- 启动链：docker-init → wget 平台 file-server entrypoint → `nohup bash /etc/waas-script/start.sh`（调 restart_comfyui.sh）→ 日志 `/var/log/waas/comfyui.log`
- restart_comfyui.sh = 平台标准重启（kill 占用 8188 → 用当前代码拉起 → 等端口就绪验证）；执行它 = 平台每次开机做的事

### 平台官方文档要点（docs.aigate.cc 查证 2026-09-09，凡哥纠正"别瞎猜，先看官网"）
- 帮助中心 URL：`docs.aigate.cc/instance-mirror/instance`（实例指南）、`docs.aigate.cc/bestPractice/aigatePlugin`（云扉ComfyUI插件）、侧边栏含 镜像/存储空间/服务端口说明/云扉OS 等
- **`/home/waas` = 独立持久化数据盘**：关机、重启、换镜像都保留；**镜像只含系统盘**（换镜像=重建系统盘，保留数据盘）；释放实例删除系统盘、不影响数据盘 → 重搭环境一律放 /home/waas
- **官方 ComfyUI 镜像**自带"云扉ComfyUI插件"：3.9TB 公模库按需秒级同步（引用式不占盘）+ 刷新 /models + 失效模型检测 + 云扉OS 跳转；**pytorch 基础镜像没有这套插件** → 自建环境里没有"公模库/刷新 models"按钮是正常的，模型直接从共享盘软链复用
- 老镜像兼容需跑平台脚本 + 客服申请"共享空间"，有风险，官方建议直接用新镜像
- 抓文档技巧：web_extract(Exa) 与 browser daemon 都可能挂；`curl -sL -A "Mozilla/5.0" <url> -o f.html` + python 正则去标签最稳

### 只读探测顺序（别急着改）
1. `ps aux | grep -i [c]omfy` → 从 cmdline 找 main.py **真实路径**（不能靠猜路径；本案例装在 /root/comfyui/ComfyUI）
2. 数据目录陷阱：`/home/<user>/ComfyUI` 可能只含 `models`+`output` 而非安装——判别：有无 main.py / 是否 git 仓库
3. `cd <真实路径> && git describe --tags` 出版本号；`git log --oneline -1` 看分支
4. `ps -o pid,ppid,cmd -p <PID>` → PPID=1 = 容器托管；重启用平台标准脚本/重启按钮，别手动裸 kill
5. 网页 SSH 代操作：命令要短、独立成条发用户粘贴（用户会把 `<>` 占位符一起粘进去 → 语法错误）

### ❌ 整体降级路线：实测失败（重要教训）
`git checkout v0.30.0` 本身成功、restart 后服务端口也起来了，但**一 Queue 采样就原生崩溃**：日志尾部整段 `Extension modules: ...` dump + `Fatal Python error: Aborted`（= 原生层崩溃特征，非普通 Python 异常）。根因：镜像插件配 0.30.1——LTXVideo 等 import `interleaved_freqs_cis` from `comfy.ldm.lightricks.model` 失败（该函数 0.30.0 没有）。**定制镜像不能整体降级**（本地便携版能跑是因为插件也是配套老版）。

### ✅ 出路（凡哥 2026-09-09 拍板，搭建进行中）
不在旧镜像上修修补补；**从 0 建干净环境**平移本地已验证组合：新开实例选 pytorch 2.8.0 + CUDA 12.8 + Python 3.12 + ubuntu2204（5090=Blackwell 必须 cu128；**勿选最新主线**——0.33.x H3 音频未修复），建 venv 装 ComfyUI v0.30.0 + **本地验证过的插件版本**（导演台锁 8/28 版，勿用镜像带的最新 9 月版），模型复用共享盘 /home/waas 软链，端口 8188。跑通一采前不算验证完成。

### Director 插件版本敏感性（2026-09-09 查证）
- 8/28 之后官方大改：9/4「混合模式每段自选 t2v/i2v/fl2v/r2v」→ 新增顶部 Model Mode 下拉（T2VA/I2VA/FL2VA/L2VA/REF2VA）+ Prompt Mode（简易/Structured）
- 简易模式给 fl2v 路径的提示词模板叫 **"FL2VA simple prompt"**：首行必须保留"参考图对齐句"（Picture 1 → 0.00s、Picture 2 → 片尾），正文字段是 `integrated_multimodal_description`（**不是** detailed_description）+ overall_soundscape + non_diegesis_music
- r2v 参考主体路径仍是六段式（subject_definitions/summary/retention_analysis + detailed_description…）→ **两个提示词区不冲突，是不同任务路径的模板**；用户跑 r2v 时按公共区+素材组区填，别理会 FL2VA simple prompt
- 本地便携版验证的 Director = 8/28 commit a148812（web/ 里没有 "FL2VA simple prompt" 字样）；云镜像自带的是 9 月新版 → 版本差异显著

### Linux 干净实例从 0 重建步骤（2026-09-09 实做，复制本地验证组合）

平台新实例选型：框架 pytorch 2.8.0 + CUDA 12.8 + Python 3.12 + ubuntu2204/2404（5090 Blackwell 必须 cu128），端口**加 HTTP 8188**。预装 base conda=`/root/miniconda3`（**torch 2.8.0+cu128、triton 3.4.0 已在 base**）；共享盘 `/home/waas`（models 全套+output）持久且新实例可见 → **模型零重下**，直接软链。

1. clone 到共享盘（持久）：`git clone --depth 1 --branch v0.30.0 https://github.com/Comfy-Org/ComfyUI.git`
2. **venv 复用预装 torch**（省 3GB 下载）：`/root/miniconda3/bin/python -m venv --system-site-packages <dir>/venv`
3. `pip install -r requirements.txt` —— ⚠️ **坑：requirements 里无版本锁的 torchaudio 会装最新 2.11.0（cu13 编译）→ 启动即 `OSError: libcudart.so.13: cannot open shared object file`**（torch 是 cu128 只有 libcudart.so.12）。修复：`pip uninstall -y torchaudio` + `pip install torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128`（torch 2.8.0 ↔ torchaudio 2.8.0）
4. 插件锁**本地验证 commit**（在 custom_nodes/ 逐个 clone + checkout；清单即本地 portable 0.30.0 里实测的那套）：
   - `HELPMEEADICE/TE-Speed-MiniMaxH3-OSS` @ `c1dacf4`
   - `kijai/ComfyUI-SolAttn_triton` @ `0e334dc`（Linux 用 base triton 3.4.0，**非** triton-windows）
   - `AIMixer/ComfyUI_MiniMaxH3_Director` @ `a148812`（8/28 验证版；9 月新版混合模式未验证音频，勿用）
   - `shuaixn/ComfyUI-MiniMaxH3DualClockSampler` @ `986f8e9`
   - `kijai/ComfyUI-KJNodes`（main；本地无 .git 无法锁 commit，本地 pyproject=1.4.9）
5. 模型软链：`mkdir -p /home/waas/ComfyUI/output && ln -s /home/waas/ComfyUI/models <ComfyUI>/models && ln -s /home/waas/ComfyUI/output <ComfyUI>/output`
6. 插件依赖循环装（无 requirements.txt 的插件跳过，triton 已在 base）；启动：`cd <ComfyUI> && unset PYTHONPATH && nohup venv/bin/python main.py --port 8188 --listen 0.0.0.0 --disable-auto-launch > log 2>&1 &`
7. 启动失败读 log 尾部分类：`Fatal Python error: Aborted` + 整段 Extension modules dump = **原生崩溃**（多为插件/版本不兼容）；`OSError: libxxx.so` / ImportError = 依赖或 API 缺失，看首因
8. **浏览器看不到工作流/模型 ≠ 没装对**（ComfyUI 新版前端 1.47.x 坑）：
   - 工作流面板只扫 `user/default/workflows/`——插件 `example_workflows/` 里的 json 不会出现在面板里 → `mkdir -p user/default/workflows && cp <插件>/example_workflows/*.json user/default/workflows/` 后刷新页面
   - 模型库侧边栏显示的是 models 目录结构：先确认 models 软链真建成了（`ls -la <ComfyUI>/ | grep models`），建软链后要**重启服务或刷新页面**才重新扫描
   - 新前端是 Library 式布局（左侧 模型库/资产/节点/工作流 图标栏），节点加载入口与旧版不同，别按旧习惯找

### 给凡哥提方案纪律（2026-09-09 纠正）
- 凡哥只走**已验证**路线。给候选修复方案前先自问"有人验证过吗？"——未验证的要当场明说"这是我的推测/候选路线，不是验证过的结论"，并先补证据（git diff / 频谱 / 官方 issue）再谈修法。本次"给 0.30.1 打补丁"纯推理方案被凡哥当场质疑，正确应对=先坦白未验证、改走证据链。
- 解释用大白话：少堆术语（"FL2VA simple prompt vs r2v 六段式"要说成"给参考图照着演 A 玩法 vs 给开头结尾自由发挥 B 玩法"），一次只讲用户当下要做的动作。
- **托管平台机制别拿通用经验猜**（凡哥 2026-09-09 二次纠正"你要不要再看一下云扉的官网说明，别瞎猜"）：涉及云厂商/平台自身约定（镜像结构、数据盘、端口映射、ComfyUI 管理插件、工作流存放），先去该平台官方帮助文档核对再下结论。

### 状态（2026-09-09 晚，续）
0.30.1 已 git checkout 还原并重启恢复；旧镜像不再当修复对象。干净新实例（5090 / pytorch 2.8.0+cu128+py3.12 / 端口 8188）从 0 搭建进度：clone v0.30.0 ✅ → venv 复用预装 torch ✅ → requirements ✅ → 5 插件锁版 clone ✅ → 依赖+triton ✅ → **torchaudio 坑已修（卸 2.11.0 装 2.8.0 cu128）→ ComfyUI 重启成功、5 插件 0 报错、8188 就绪（已验证）**。待回读确认：模型软链/工作流复制命令执行结果 + 浏览器面板显示 + 一采音频频谱——通过前不视为全链路已验证。
