# H3 高清成片最终路线（2026-09-09 三期）：外部超分实测 + LTX2.5 跨模型放大

承接 SKILL.md「高清/2K 放大路线」与「官方原生模板加速与生态更新」两节。三期结论：**Director 2K 二采(OOM) 与 官方 2K 直出(悬崖) 都放弃；5090/32GB 正路 = 低清(≤0.7MP)直出 + 外部放大**。放大有两个选项：RTX VSR（纯超分，快但无参考保真）与 LTX2.5 跨模型重绘放大（UP 实测主推，带 IC-LoRA 参考图保脸）。

## 一、社区权威实测数据（5090，2026-09 查证）

### wan2-7.io《MiniMax H3 Requirements: 36 FL2VA Runs》（5090/32GB/128GB RAM/ComfyUI 0.30.0/8s=192帧）
- **峰值 VRAM 31,745–31,798 MiB ≈ 31.8GB——三种模型（bf16/int8/pruned）全打满 32GB**。pruned 只省磁盘/RAM（峰值 77.6GiB RAM），**不省峰值显存**。
- 8s 档时间：0.3MP≈2min / 0.5MP 4m17s / 0.7MP 7m26s（**最值档**）/ 1.0MP 13m49s（+86% 时间细节增益小）。
- 该站域名 wan2-7.io 只是博客名（平时测 Wan），该文 100% 是 MiniMax H3 实测。

### ai-muninn.com（5090 系列，H3 + VSR 完整工作流实证）
- **2K 直出（1080p 1920×1080, 158帧/14步）= 12,599s（3.5 小时）——分辨率悬崖**：864×480=105s → 720p=239s（近线性）→ 1080p(5×像素) = 120× 暴涨。>720p 后某机制（疑显存换页灾难）致指数爆炸。
- Part2《Twice as Fast》：15s 1080p 成片（362帧+音频）总 625s→**314s**，栈：20→14 步(−18.9%) + SageAttention 2.2(−18.8%) + **RTX VSR 换 RealESRGAN(−23.7%)**。ffprobe：1920×1080·24fps·362帧·stereo·15.083s（音频同轨保留）。
- 管线 = H3 native 864×480(或 960×540) 一采 → VSR 2×（超分腿仅 **11.2s**/362帧 vs RealESRGAN 109s）→ ffmpeg 补到 1920×1080。540 高度有 bug（latent height//16 → 528）需 ImageScale bilinear 校正。
- **纯超分保真边界（凡哥质疑成立，作者原文承认）**："VSR does invent detail — it can't recover information the source never resolved. A face occupying a few dozen pixels... face-shaped rather than that specific person's face." 2× 小幅放大安全；模糊小脸救不回（重拍 close-up 比拉分辨率便宜）。wide shot 脸 34,000 有效像素 vs close-up 226,800。
- RTX VSR 的 quality 坑：标准档（LOW/MEDIUM/HIGH/ULTRA）是"压缩伪影抑制"族，**对无压缩伪影的扩散画面会把真实纹理当伪影删 → 比原片糊**；须用 **HIGHBITRATE_HIGH**（跳过伪影抑制）。

## 二、RTX VSR 云端部署与实测（2026-09-09 凡哥云端实测）

- 插件：`Comfy-Org/Nvidia_RTX_Nodes_ComfyUI`（git clone 到 custom_nodes；节点 `RTX Video Super Resolution`，官方 example_workflows/rtx_video_upscale.json = LoadVideo→VideoInfo(取图/mask_depth)→RTXVideoSuperResolution→CreateVideo→SaveVideo）；依赖 `pip install nvidia-vfx`（0.1.0.1）。
- 实测：864×480 15s 片 → 2× 输出 **1728×960·362帧**（尺寸放大成功，~20s/片；二次 Queue 缓存命中 ~6s）。
- **官方原版 quality 下拉只有 LOW/MEDIUM/HIGH/ULTRA**（无 HIGHBITRATE）。补丁（照 ai-muninn 一行改动）加 HIGHBITRATE_HIGH：
  - `__init__.py` 44 行 `options=["LOW","MEDIUM","HIGH","ULTRA"]` → 追加 `"HIGHBITRATE_HIGH"`
  - 74-78 行 quality_mapping 追加 `"HIGHBITRATE_HIGH": nvvfx.effects.QualityLevel.HIGHBITRATE_HIGH,`
- 补丁后重启 ComfyUI + 浏览器刷新（下拉随节点 schema 更新）。
- ⚠️ 结论纪律（凡哥纠正）：纯超分（RTX VSR/RealESRGAN/SeedVR2/FlashVSR）**无角色参考**，对 H3 已模糊的中远景脸 = 脑补"脸形"非还原"本人"。凡哥测试后判"比原片还糊"（ULTRA 删纹理）——**2× 超分只适合近景/脸够大的片**；做剧要保脸 → LTX2.5 路线（下节）。

## 三、LTX2.5 跨模型放大（UP「啦啦啦的小黄瓜」B站教程 BV1CT8v6JEdw，5090 实测主推）

### 原理
LTX2.5 自带二阶段采样 → 第二阶段挂 **Spatial Upscaler（latent 2×）**；放大时：**音频作为引导传入**（口型对得上）+ **IC-LoRA（ingredients 多图参考）注入人物/物件/背景特征** + 低降噪重绘 → 同时完成**去模糊 + 保人物一致 + 2× 放大**（还能插帧 24→60fps）。解决纯超分"无参考崩脸"。
实测（5090）：8s/192帧 2× 放大 3分14s；10s 544×960→1080p 3分43s、显存 **25.9GB**。

### 局限（UP 自述）
- LTX2.5 高动态差：剧烈运动/镜头急拉近/闪现 → 像素模糊修不了（60fps 好些）
- 中景人脸"有一点点变样"（比 H3 好但非 100% 同脸）
- 提示词写"视频怎么随时间变化"（**[0s-2s] 时间段格式**），**禁止写"高清放大/去模糊"**；参考图长宽比尽量对齐原视频；原视频无提示词 → GPT/豆包反推画面内容
- 放大前原视频若已 2K → 先缩放再放大（4K+ 跑不动）

### 工作流参数（UP json：D:\Hermes\attachments\LTX2.5放大视频.json，31 节点/48 links）
- 采样：euler_ancestral / simple / **3 步 / denoise 0.25** / CFG 1（低降噪轻重绘）
- 模型链：UNETLoader(ltx-2.5-22b-distilled int8) → LoraLoaderModelOnly(**ltx-2.3-22b-ic-lora-ingredients-0.9**, strength 0.9) → CFGGuider/BasicScheduler
- 放大：VHS_LoadVideo(force_rate 24, 可改 60 插帧) → VAEEncode → **LTXVLatentUpsampler**(ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0) → LTXAddVideoICLoRAGuide(参考图 LoadImage→RepeatImageBatch(按帧数)→IC guide)
- 音频：LTXVAudioVAEEncode(audio-vae) → LTXVConcatAVLatent 与视频 latent 合并 → SamplerCustomAdvanced → LTXVSeparateAVLatent → LTXVAudioVAEDecode / LTXVCropGuides(裁回原尺寸) → VAEDecodeTiled → CreateVideo/VHS_VideoCombine

### 模型清单（6 文件，全部官方 HF 仓库，约 25GB）
| 文件 | 仓库 | 落盘 |
|---|---|---|
| diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot | Lightricks/LTX-2.5 | models/diffusion_models/LTX2/ |
| text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot | Lightricks/LTX-2.5 | models/text_encoders/LTX/ |
| vae/ltx-2.5-video-vae-bf16 | Lightricks/LTX-2.5 | models/vae/LTX-Kijai/ |
| vae/ltx-2.5-audio-vae-bf16 | Lightricks/LTX-2.5 | models/vae/LTX-Kijai/ |
| latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0 | Lightricks/LTX-2.5 | models/latent_upscale_models/ |
| ltx-2.3-22b-ic-lora-ingredients-0.9.safetensors | Lightricks/LTX-2.3-22b-IC-LoRA-Ingredients | models/loras/LTX/ |

（子目录名保持 UP json 引用一致：LTX2/LTX/LTX-Kijai。注意要 distilled 版非 dev 版。）

### 下载方法（云上无外网 HF，走国内镜像 hf-mirror.com）
```bash
export HF_ENDPOINT=https://hf-mirror.com
# python: huggingface_hub.hf_hub_download(repo_id, filename, local_dir=<父目录>)；huggingface_hub 读 HF_ENDPOINT ✓
```
可用 ComfyUI venv 的 python + huggingface_hub（ComfyUI 依赖自带）。完整可跑脚本（6 文件逐一下载打印进度）见视频学习笔记/本次交付命令。下载 ~25GB 用 nohup 后台 + 日志。

## 四、其它外部超分资源（datasets 公模库已见，未实测）
/datasets/ComfyUI/models/ 下有 SEEDVR2、FlashVSR/FlashVSR-v1.1、Aura-SR、diffbir、invsr、uso、sharp、upscale_models 等超分模型目录——若走纯超分路线先查这里免下载。datasets **无 LTX2.5 任何模型**（diffusion/text_encoder/vae/latent_upscale/IC-lora 全空）。

## 视频学习资源位置（本次）
- B站视频（已下载）：D:\数字资产\云电脑工作流\learn\绝了！MiniMaxH3高清放大效果这么好！脸崩直接修复！ComyUI MiniMaxH3高清放大本地实测教程！.mp4（15:46）
- 完整转写（faster-whisper medium）：同目录 transcript.txt
- 抽帧：同目录 frames/frame_001-047.jpg
- UP 工作流 json：D:\Hermes\attachments\LTX2.5放大视频.json（31 节点，UI 格式可拖入）

## 五、LTX2.5 落地执行补充（2026-09-09 会话尾，云上部署实证）

### HF gated 仓库下载（Lightricks 官方全 gated——实测结论）
- **Lightricks/LTX-2.5、Lightricks/LTX-2.3-22b-IC-LoRA-Ingredients 都是 gated**：hf-mirror resolve 直链返回 401 `Access ... is restricted. You must have access to it and be authenticated`。
- **hf-mirror 不转发 gated 授权**——带上 HF 官网 Read token（`Authorization: Bearer hf_xxx`）仍 401；hf-mirror 只镜像公开仓库。
- **正解 1（公开文件）**：找非 gated 搬运镜像。实测 `comfyicu/LTX-2.5`（HF 搬运号，保留官方仓库结构）**匿名 curl 直链 200** → LTX2.5 的 5 个文件全部从 `https://hf-mirror.com/comfyicu/LTX-2.5/resolve/main/<仓库内路径>` 下载成功（curl -L，nohup 后台）。搬运号仓库结构若与官方一致，可直接替换 repo 名。
- **正解 2（gated 文件，IC-LoRA 无公开镜像只能此路）**：HF 官网注册/登录 → 打开模型页点 **Agree and access repository** → `huggingface.co/settings/tokens` 新建 **Read** token → 带 token 从官网/hf-mirror 都下不了时，改**浏览器直接下载该文件**再传云。注意：网页端 tokens 页预设默认 full-access，创建时改选只读。
- 实测下载路径：venv python 的 `huggingface_hub.hf_hub_download` 在云上失败（疑似代理/库问题），**curl 直链最稳**。

### UP 工作流依赖两个插件（云端缺失会整图红）
- `Lightricks/ComfyUI-LTXVideo`（提供 LTXAddVideoICLoRAGuide / LTXVLatentUpsampler / LTXVConcatAVLatent / LTXVAudioVAE* / LTXV* 全套，节点在插件 `.iclora` 等模块，**不在 ComfyUI 内核**——内核只有 comfy_api_nodes/nodes_ltxv.py 的部分 LTX 节点）
- `c0untFloyd/ComfyUI-VideoHelperSuite`（VHS_LoadVideo / VHS_VideoCombine）
- 装法：custom_nodes 下 git clone + pip install -r requirements.txt + 重启。

### IC-guide 多参考图标准接法（官方插件源码 iclora.py 实证）
- `LTXAddVideoICLoRAGuide.image` 输入**原生支持多帧参考**（描述原文 "Adds one or more conditioning frames... Supports both single images and multi-frame videos"）：多张图 = 参考视频帧序列，从 `frame_idx`（默认 0）注入 latent 开头；逐帧 VAE encode → append_keyframe。UP json 的 RepeatImageBatch(复制单图到总帧数) 只是"单图全片条件"的写法，**多图时不要 RepeatImageBatch**。
- 多图接法（凡哥拍板方案，不做拼图/裁切）：`LoadImage×N → ImageBatch(Join Images) 两两串联合并 → IC guide.image`。**ImageBatch concat 要求各图同尺寸**（不一致会报错——参考图统一用资产库同批 16:9 图）。
- 已交付 `D:\数字资产\云电脑工作流\LTX2.5放大视频_3参考图_云版.json`（34 节点/50 links/自检 0 错误：3×LoadImage + 2×ImageBatch → IC-guide，保留 UP 采样参数 3步/denoise0.25/euler_ancestral）——**插件装完、模型下载完前尚未实测运行**，多格多图是否被 IC 正确解析待凡哥云端验证后定稿。
- 凡哥 OPC 取向（2026-09-09）：放大环节**场景不需参考、只有人脸会崩** → 参考图只喂角色图；放大参考图 = OPC 资产库现成角色资产图（按镜造型状态调取），OPC 无需新增"洗图"工序。
