---
name: comfyui-env-ops
description: 凡哥换ComfyUI版本/模型跑不动或LTX·H3部署时触发。版本兼容矩阵与内核/插件失效判定。
---

# ComfyUI 环境运维（跨内核/跨机器）

ComfyUI 大版本升级后最常见的坑不是模型文件，而是**内核与模型/插件/torch 的版本矩阵**。核心纪律：先取官方出处与完整日志，禁止先猜"显存/分辨率"。本地 Windows 对照见 comfyui-update（凡哥自建，不可代改）。

## 版本兼容矩阵（2026-09 实测，官方出处）

| 需求 | 版本 | 出处/依据 |
|---|---|---|
| LTX-2.5（22B/VAE 48ch）| ComfyUI ≥ **0.32.0** | Comfy-Org 官方博客《LTX-2.5 Day-0 Support》 |
| ComfyUI 0.35.0 | torch **cu130+**（RTX 20 系以上硬性）| ComfyUI 启动日志原文 |
| torch cu130 全家 | torch 2.14.0 / torchvision **0.29.0**（0.x 独立号）/ torchaudio 2.11.0 | pytorch cu130 源实测 |
| sage 加速（官方内置）| 启动参数 `--use-sage-attention`（免第三方插件）| ComfyUI 内置 attention.py |

关键坑：
- **判断 VAE 文件类型用结构不用文件名**：safe_open 读 `decoder.conv_out.weight`——video VAE 3D（如 [3,512,3,3] 级）、audio 1D（[48,256]）。镜像仓库文件名可能骗人。
- `pip install torch` 不写 `-U` = 不升级已装包 → torchaudio 升 cu130 但 torch 留旧 → `libcudart.so.13` 崩。torch 三件套版本号体系不同步（torchvision 0.x），按 torch 号猜必错。
- 大 wheel 下载必须 `nohup ... &` + tail 轮询；前台 pip 会长时间无输出占死 SSH。

## 内核大版本升级 → 第三方加速插件失效（0.35 实测）

- ComfyUI 0.35 重构 `comfy/ldm/minimax/model.py` → 按旧内核 monkey-patch 的插件全废：
  - TE-Speed：静默失效（日志 `no block_loop hooks`）
  - ComfyUI-SolAttn_triton：`Fatal Python error: Aborted`（栈顶 `_morton_h3.py` → torch `module.__setattr__`）。triton 3.4/3.8 都崩同点 = 与 triton 版本无关，是内核结构不匹配。
- **官方替代加速 = `--use-sage-attention`**（内置；sageattention pip 包即可，sageattn3 为 Blackwell 可选增强）。
- **aimdo 0.5.x + sage/稀疏注意力 = 已知 OOM**（官方 issues #16144 H3 内存泄漏、#15759 VRAM grow failed）。症状特征：`VRAM grow failed: N bytes` 时 GPU 反而空闲 30GB+ = aimdo 记账 bug 非真 OOM。方向：去掉 sage flag 用纯官方模板（#16144 用户 bypass 稀疏节点即正常；按"一次只变一个变量"复测确认）。
- 日志纪律：`退出 134 / Fatal Aborted` = C/CUDA 层硬崩，Python 无 ERROR 行；必须 `awk '/got prompt/{b=""}{b=b"\n"$0}END{print b}' log | head` 取完整崩溃段，栈顶异常在 tail 窗口外。**先看完整日志再断言**。

## LTX 插件部署坑：kornia 0.8 移除 pyramid.pad

Lightricks/ComfyUI-LTXVideo 首次安装后 IMPORT FAILED（其余插件正常）：`pyramid_blending.py` 里 `from kornia.geometry.transform.pyramid import pad`——kornia 0.8.x 删了该 pad。修（不降 kornia）：去掉该 import，文件内加兼容函数 `def pad(x,p,mode="constant",value=0.0): return F.pad(x, tuple(p), mode=mode, value=value)`。

## 排障流程（凡哥纠正：先取证再断言）

1. 崩溃先取完整日志段：`awk '/got prompt/{b=""}{b=b"\n"$0}END{print b}' log | head`——tail 只见栈尾，真实异常在段首（SolAttn 崩因在 `_morton_h3.py`）。
2. **先搜官方/社区 issue 再动环境**：特征怪（如报 OOM 但显存空闲 30GB+、升版后新报错）→ 第一动作 GitHub issues 搜 `"<报错串>" <组件/模型名>`。aimdo+sage 冲突即官方 #16144/#15759。
3. 分辨率/显存/版本断言前必须有实测或官方出处（凡哥：『你确定吗？依据是什么？』『又是你脑补出来的吧？』）。
4. **模型/版本发布传闻只认官方源**：凡哥问"某新模型怎么切换"时，先跑官方 API 列表（`curl https://api.deepseek.com/models -H "Authorization: Bearer $KEY"`）+ 官方文档（api-docs.*）。第三方新闻站（groundtruth.day / byteiota.com / alextech.ai 这类）常是内容农场、互相转引，**不能当事实转述**。实例：所谓 "DeepSeek V4.1 Flash 今天12:00 上线并自动路由 v4-pro" 全是第三方站说法；实测官方 /models 只有 `deepseek-flash` / `deepseek-v4-pro` / `deepseek-v4-flash-vision-exp`，官方文档无 v4.1——传"今天几点自动切换"= 把传闻当事实，必被当场质疑。
5. 一次只变一个变量；`退出 134 / Fatal Aborted` = C/CUDA 硬崩，Python 无 ERROR 行。
6. **能从源码读出来的结论，别拿一次真跑去换**（一次 20GB 模型的试跑成本是十几分钟 GPU + 一轮上下文）。本次两个问题都是读 `custom_nodes/<插件>/*.py` 直接定论的：① 「整轨音频是条件还是只取前 N 秒」→ `h3_unified.py:531-537`；② 「生成时长谁说了算、输出音轨是谁的」→ `h3_unified.py:80-116`。**先 grep 节点源码，读不出再跑**；读出来的结论要标「已确认（源码）」而不是「已实测」。
7. **★ 工作流身份与工作流故障：先查 UP 官方信息，不要自己推方案**（凡哥 2026-09-18 纠正：『你去看这个 up 主的官方信息，从那里找方案修，**不要自己瞎试**』；同一轮还纠正『**不是小黄瓜的**，我们的这个工作流的特点是有提示词优化功能的，你忘记了？』）。
   - **身份（作者/版本）从工作流 json 的 `MarkdownNote` 节点读**（写死了 `【作者】`、教程链接、网盘），别凭印象、别信旧笔记：
     ```python
     import json
     d = json.load(open(WORKFLOW, encoding="utf-8"))
     for n in d["nodes"]:
         if n["type"] == "MarkdownNote": print(n.get("title"), "|", str(n.get("widgets_values"))[:800])
     ```
   - 本项目所用 UP 工作流作者 = **Astral星芒**（space 176339505），**辨识特征＝带本地提示词优化（QwenTE / comfyUI-llama-TE）**；「啦啦啦的小黄瓜」= 另一套 LTX2.5 放大方案的作者（已被凡哥否掉），**两套不可混记**。
   - **故障根因三源对齐**才给方案：① UP 视频教程 ② json Note / 作者主页 / 网盘说明 ③ 插件源码（参数定义与 tooltip）。自创结论只能标「待验证」。
   - 反面教材：二采暴显存崩，曾自创「cudaMallocAsync 高压崩 → 加 `--disable-cuda-malloc`」，被凡哥打回；真根因是 UP 早讲过的 **`short_edge_max = 0`（参考图不缩放）**，见 `av-generation-troubleshooting/references/h3-refimage-scaling-vram-crash-2026-09.md`。

## LTX IC-guide 多参考图（官方源码核实）

`LTXAddVideoICLoRAGuide.image` = 参考帧序列（支持多帧）。多参考图标准接法：多个 `LoadImage` → `ImageBatch`（Join Images）串联合并成 N 帧 batch → 直连 guide（frame_idx=0）。要求各参考图同尺寸。放大倍数由 upscaler 模型定死（官方仅 x2 模型，工作流无倍数旋钮）。

## 任务残留与批量生产

ComfyUI 任务中断/失败后模型不卸载（`0 models unloaded`）→ 下任务 OOM。批量/平台接法：每任务前 `POST /free`（`{"unload_models":true,"free_memory":true}`），封装在 worker 层一次，客户无感。

## 云端装件与运行可见性（2026-09-10 实测）

### 先查公模库，再下载
装模型前先 `find /datasets -iname "*<关键词>*" 2>/dev/null | head`——公模库（`/datasets/ComfyUI/models/...`）常有现成文件（例：`minimax_h3_turbo_v4_step600_ema.safetensors` 公模库已有）。有就软链：`cd <目标目录> && rm -f <文件>; ln -s /datasets/... <文件>`。**软链前必须先 rm 掉 curl 中断留下的半截文件**，否则占位导致假成功。没有才下载：先 `curl -sIL ... -o /dev/null -w "%{http_code}"` 验 200，下完 `ls -la` + `du -h` 验真实大小（防 150B 假成功）。

**大文件（>5GB）判"下完没有"必须用字节对比，不能看 `du -h`**——20GB 文件差 1.3GB 时 du 会四舍五入成看起来很接近的数，凡哥会问"是不是没进展/下完了吗"，你要能立刻给确定答案：
```bash
# ① 先取官方精确字节（一次）
curl -s "https://hf-mirror.com/api/models/<repo>?blobs=true" | python -c "import sys,json;[print(f['rfilename'],f.get('size',0)) for f in json.load(sys.stdin)['siblings']]"
# ② 下载中/完成后对比（进度百分比）
S=$(stat -c%s <文件>); echo "当前 $S / 目标 <字节> = $((S*100/<字节>))%"
ls -la <目录>   # 第一个文件到齐后脚本才会开始下第二个 → mmproj 未出现 = 主模型仍在下
```
多文件串行下载（`curl A && curl B`）时，**后一个文件没出现就是前一个没下完**，这是最快的判断信号。下完再 `grep` 一下无 `IMPORT FAILED` 后重启实例让新件被扫到。

**公模库没有 → 先溯源发布源再下**（不要只在 Manager 界面点下载）：

1. 搜 HF 仓库：`curl -s "https://hf-mirror.com/api/models?search=<关键词>" | python -c "import sys,json;[print(m['modelId']) for m in json.load(sys.stdin)[:20]]"`
2. 看仓库文件与真实大小：`curl -s "https://hf-mirror.com/api/models/<repo>?blobs=true" | python -c "import sys,json;[print(f['rfilename'], f.get('size',0)//1048576,'MB') for f in json.load(sys.stdin)['siblings']]"`
3. hf-mirror `resolve/main/<文件>` 下载 + `ls -la` 验大小

**工作流引用的文件名必须精确匹配**：工作流写 `minimax_h3_video_vae_int8_convrot.safetensors`，你手里只有官方的 `minimax_h3_video_vae_fp16.safetensors` → 加载节点里选不到、报缺模型。官方 `Comfy-Org/MiniMax-H3` 只发 fp16 video VAE + fp32 audio VAE，**int8_convrot 量化版属第三方源**（见 `references/h3-model-sourcing.md`）。凡哥问"这个模型有没有"时的正确回答顺序：公模库 find → 本地模型目录 find → HF 搜源（三步都要给依据，别只说"没有"）。

**整个目录可软链**：`ln -sfn /datasets/ComfyUI/models/layerstyle /home/waas/ComfyUI/models/layerstyle`——LayerStyle 那批模型（抠图/超分/人脸等）整目录软链最省事，插件自动扫 `models/layerstyle/`。

### 补齐工作流缺失插件
1. 先验仓库存在：`curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/<owner>/<repo>`（200 才算数，不凭名字拼）
2. 批量 clone 进 `custom_nodes`，逐目录有 `requirements.txt` 就装
3. 重启后 `grep -iE "IMPORT FAILED|<关键插件名>" comfyui.log` 确认加载

⚠️ **不要用 `| tail -1` 收 clone 输出**——它会把报错一起吞掉：一次网络抖动就变成"5 个插件全没装上"却只看到一行正常字样（凡哥原话：『装了个寂寞』）。逐条打印并**验目录文件数**：
```bash
for r in "<owner>/<repo>"; do n=$(echo $r | cut -d/ -f2); git clone "https://github.com/$r" "$n" 2>&1 | tail -3; [ -d "$n" ] && echo ">>> $n OK ($(ls $n | wc -l) 个文件)" || echo ">>> $n 失败"; done
```
安装结果**从不以 exit 0 为准**：`ls -d <目录>` + 文件数 >0 才算装上。
实例（UP 参考/放大工作流缺件）：`chflame163/ComfyUI_LayerStyle`、`pythongosssss/ComfyUI-Custom-Scripts`、`LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler`、`oufeixinxinren/ComfyUI-MiniMax-ContextIR`、`rgthree/rgthree-comfy`（`Fast Groups Bypasser` 属 rgthree，装它即可）。另需 `ltdrdata/ComfyUI-Manager`（节点管理）+ `crystian/ComfyUI-Crystools`（顶栏实时监控 GPU/显存/内存 + 一键释放缓存，一个顶两个）——凡哥要"下载数最多、不冷门"时首选这两个。

#### 依赖缺失诊断闭环（LayerStyle 实例，2026-09-10）

症状：插件目录在、日志却 `X.X seconds (IMPORT FAILED): .../ComfyUI_LayerStyle`。
**别一轮一轮试 package**——`requirements.txt` 会漏包（LayerStyle 连缺 `skimage`、`blend_modes`、`blind_watermark`、`wget` 四轮）。一次做全：

1. 取报错：`grep -B5 -A25 "Cannot import.*<插件名>" comfyui.log | tail -35` → 看 `ModuleNotFoundError: No module named 'X'`
2. 全量装作者清单 + 常见漏网：`cd <插件目录> && <venv>/bin/pip install -r requirements.txt <补充包>`
3. **扫描源码列真实缺失**：`<venv>/bin/python scripts/scan_missing_node_imports.py`（本 skill 附带）——输出 `还缺: [...]`
4. 只装第 3 步列出的，再扫描确认 `还缺: 无 ✅`，最后才重启验证

扫描结果的三个必须知道的坑：
- **虚报**：`comfy` / `folder_paths` / `nodes` / `node_helpers` 是 ComfyUI 运行时模块，从 custom_nodes 目录跑 python 时找不到是正常的——脚本已排除，**别去 pip 装**。
- **模块名 ≠ pip 包名**：`skimage`→`scikit-image`、`blend_modes`→`blend-modes`、`cv2`→`opencv-python`、`blind_watermark`→`blind-watermark`、`wget`→`wget`。
- 装完先单测 import（`<venv>/bin/python -c "import X, Y; print('OK')"`）再重启，省一轮 40 秒启动。

#### 配套模型放置目录（别只装插件不装模型）

- **H3 Latent Upscaler**（LBH-123-AI）：checkpoint 放 `ComfyUI/models/latent_upscale_models/`，HF 仓库 `LBH-123-AI/Minimax_h3_latent_Upscaler`，三版本 `minimax_h3_latent_upscaler_3d_{bf16,fp16}.safetensors` / `_fp32.pth`——**推荐 bf16**（省显存够精度），同一权重 2D/3D 节点通用（loader 自动识别架构）。
- **MiniMax-ContextIR**（8 节点全家桶：Unified to Video / Context IR / Audio Lock / Media Loader / Reference Splitter / Concat AV Latent 等）：不需新模型（复用官方 H3 UNET + Qwen3-VL CLIP + video/audio VAE）；媒体加载需 PyAV 或 ffmpeg 之一（`python -c "import av"` / `which ffmpeg` 验一个即可）；Context IR 节点才需 MiniMax 云 API key（可选功能）。
  - 报错 `ValueError: api_key is required for external LLM calls.`（节点 `MiniMaxH3MultimodalChat`，栈 `h3_chat_api.py`）→ 整条 prompt 秒退（`Prompt executed in 0.09 seconds`）。两条路：① 配 MiniMax 云 key；② **换本地方案 `tl2012tl/comfyUI-llama-TE`**（177★，本地 GGUF 做图片反推 / 写提示词 / 多轮对话，零 API 费用，UP 工作流即用此路）。
  - `comfyUI-llama-TE` 部署要点：核心依赖 `llama_cpp`——**必须装 JamePeng fork 的预编译 wheel，不是 PyPI 的 abetlen 原版**（原版不支持 Qwen3.5+，会报 `不支持 Qwen35ChatHandler`；原版已装的还要先 `pip uninstall -y llama-cpp-python`）。wheel 选名看 `JamePeng/llama-cpp-python` releases：按 `cu###` × `cp3XX` × `linux_x86_64`，Linux 有 cu131/cu128/cu126/cu124（无 cu130）；模型 = GGUF 主模型 + 对应 `mmproj`，放 `ComfyUI/models/LLM/`（如 `Qwen3.8-27B-Q3_K_M.gguf` + `Qwen3.8-mmproj-BF16.gguf`、`qwen3.6-vl-35b-a3b-q4_k_m.gguf` + `mmproj-qwen3.6-vl.gguf`）；节点 = `Qwen/Gemma4 TE 模型加载器` + `图像推理` / `多轮对话` / `Skill加载器`（内置 `h3-prompt-writing` 等 H3 Skill，能按 T2VA/I2VA/FL2VA/Ref2VA 规则产 H3 提示词）。装完先查公模库现成 GGUF：`find /datasets -iname "*.gguf"`。
  - **实测补充（2026-09-10）**：节点类名 = `QwenTE_ModelLoader` / `QwenTE_ImageInfer`（还有多轮对话、Skill 加载器）；工作流里模型路径写成 `Qwen\xxx.gguf` 时 = **子目录** `models/LLM/Qwen/`，放错层级节点会"选不到模型"。**下载时用 `-o` 直接存成工作流要的名字**（URL 用 HF 长名，本地存短名），打开工作流即匹配、不必手改节点。`QwenTE_ImageInfer` 支持哪些图片输入（`图片` / `图片2` / `图片3`）**要 grep 插件源码确认**，不支持的多图输入会执行即报错。GGUF 主模型 20GB 级，见 `references/h3-model-sourcing.md` 的 Qwen LLM 段。

### 进度可见性：界面没进度条 ≠ 卡死
第三方节点（tiled sampler / latent upscaler / turbo sampler）不上报进度，UI 只给内置节点画进度条。判断在跑还是挂了：
- `tail -f /home/waas/h3-0300/comfyui.log`——阶段行（`Requested to load X`）、采样进度（`3/3 [07:45<00:00]`）、`Prompt executed in 00:12:01` 都有
- `watch -n 3 nvidia-smi`——GPU-Util 高 + 显存占用大 = 在算；0% + 显存空 = 没跑起来
- 取件：`ls -lat /home/waas/ComfyUI/output/ | head -5`

### "第二次跑不采样" = seed 没换（缓存命中，不是 bug）

现象：日志连续 `got prompt`，却每次 20~30 秒就 `Prompt executed`、**完全没有采样进度**（第一次正常跑了 12 分钟）。原因：输入与 seed 都没变 → ComfyUI 判定结果无变化走缓存，不重算。**批量出片每镜/每次必须换 seed**——这是 OPC 批量的固化纪律，种子不换等于白跑。排查顺序：先确认 seed 是否变化，再怀疑环境。

### MiniMax H3 Turbo（larryvrh 官方节点，2026-09-10 核实）
- 节点仓库 `larryvrh/ComfyUI-MiniMax-H3-Turbo`（Turbo LoRA + Turbo Sampler + low_vram 开关）
- LoRA 仓库 HF `larryvrh/MiniMax-H3-Turbo-Lora`，**v4 = `minimax_h3_turbo_v4_step600_ema.safetensors`（当前最强：静态/细节/手脸优于 v1）**，放 `loras/`
- 用法：`MiniMax-H3 Turbo LoRA`（MODEL→MODEL）+ `MiniMax-H3 Turbo Sampler` → SamplerCustomAdvanced；scheduler `simple`、**4~8 步**、strength 1.0
- 节点自动适配 pruned 主模型；新 ComfyUI 原生处理视频+音频双时间表 → 少步数音频仍干净
- ⚠️ 与旧记录（working-with-fange #87/#92/#93 的手动键名转换版、Ref2VA 架构不兼容）不是同一条路：v4 走官方节点包，**Ref2VA/全能参考兼容性尚未实测**——用时按"一次只变一个变量"验证

### H3 融合主模型 / 量化件（UP 工作流常用，2026-09-10 核实；**UP ＝ Astral星芒，不是小黄瓜**）
- **Singularity 融合版**（UP 主称可有限缓解人物油腻、快速动作变形）：HF `WarmBloodAban/Minimax-h3_Singularity`
  - `Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors`（**19996MB ≈ 20GB**，常用）/ `Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors`（32429MB 完整版）
  - **公模库 `/datasets/ComfyUI/models/diffusion_models/` 已有 pruned 版** → 软链即用，零下载
  - 用法：**替换工作流的 UNET/diffusion_models 加载项**（是主模型不是 LoRA），放 `models/diffusion_models/`
- 同源还有 `Singularity LTX-2.3 OmniCine Preview v0.1.safetensors`（LTX 2.3 融合 LoRA，公模库 `loras/`）
- 全部 H3 相关模型（主模型/VAE/text encoder/latent upscaler/turbo LoRA）的来源仓库、大小、公模库路径、放置目录总表：`references/h3-model-sourcing.md`

### H3 低显存档（16GB 级）与 pinned memory（2026-09-11 源码核实，本机 Windows）

**16GB 显存档的现实配置**（社区口径，非本机实测）：pruned INT8 主模型 + **NVFP4/AWQ 编码器**（14.61GB，别用 int8_convrot 25.28GiB）+ Turbo 4~8 步 + sol-attn；实测参考 `5080 16GB 跑 960×544`、`4090 Laptop 16GB 跑 960×540/5s`。速度量级 ~5–6 分钟/5s@1MP。
官方四件套字节（Comfy-Org repack，配 UP 工作流时按此核对）：DiT `pruned_int8_convrot` 20,970,379,616（19.530GiB）/ 编码器 `nvfp4_awq` 15,687,142,551（14.610GiB）/ video VAE fp16 5,207,808,496（4.850GiB）/ audio VAE fp32 605,254,808（0.564GiB）。

**pinned memory 是低内存机器的真正卡点，且虚拟内存救不了它**：
- 源码 `comfy/model_management.py`：
  - `MAX_PINNED_MEMORY = get_total_memory(cpu) * 0.40`（**Windows**，注释：系统锁定上限约 RAM 的 50%；Linux 为 0.90）
  - `pinned_hostbuf_size(size) = max(0, int(min(size, MAX_PINNED_MEMORY) * 2))` ← **×2** 双缓冲
- 例（32GB RAM 机跑 19.53GiB DiT）：MAX = 31.4×0.40 = **12.56 GiB** → 请求 12.56×2 = **25.12 GiB** 锁定内存 > Windows ~50% 上限 → 大概率 `logging.warning("Pin error.")` 后**回退普通内存**（慢，但源码有 `discard_cuda_async_error()` 兜底，**通常不硬崩**，别把"会 OOM 崩"当定论）。
- ⚠️ 第三方文章常引"为 transformer 申请 39GB 锁定内存"——那是 `19.53 × 2`，**只在 RAM ≥ 48.8GiB 时成立**（那时 `min(size,MAX)` 取到 size）。**别把这个数直接套到小内存机器上**。
- **`--disable-pinned-memory` 才是低内存档的正解**：关掉后 `MAX_PINNED_MEMORY<=0` → `pin_memory()` 直接 `return False`，全部走**可分页内存** → 这时**页面文件（虚拟内存）才真正兜底**。反之开着 pinned，页面文件对锁定内存零帮助（page-locked 定义上不可换出）。
- 代价：虚拟内存换页与读模型文件**抢同一条盘**——先确认 pagefile 所在分区与模型盘是否同一物理盘（`Get-Partition | ? DriveLetter` 看 DiskNumber），同盘则速度雪上加霜。
- 检查本机：`powershell "Get-CimInstance Win32_PageFileSetting|select Name,InitialSize,MaximumSize"` + `Win32_OperatingSystem` 的 `TotalVirtualMemorySize`（= 提交上限 = 物理 + pagefile）。

### UP Swan鹄仙「H3 长视频 MV」工作流（BV1bq8H6pEY2）缺件来源表（2026-09-11 核实）

工作流 UI 格式 47 节点/6 组（Models / Sampling / Conditioning / Decoding and create video / User Inputs / context组）。**查缺件别只 grep `"Class":`**——0.3x 起核心节点用 `IO.Schema(node_id="X")` 写法，旧的正则会**误报缺失**（本次把 `ComfyMathExpression`/`PrimitiveStringMultiline`/`ResolutionSelector` 误判为缺，实际在 `comfy_extras/nodes_math|primitive|resolution.py`）。四路匹配：`node_id="X"` / `"X":` / `^class X` / `"X",`。

| 缺失节点 | 来源插件 | 备注 |
|---|---|---|
| `MiniMaxH3MotionContext` `/Trim` `/SaveLatent` `/LoadLatent` | `NikoDemon80/ComfyUI-H3-Motion-Context` | ⚠️ **v0.4.0+ 要 ComfyUI ≥0.34.0**；`≤0.33.4` 只能用 **v0.3.1**（作者 CHANGELOG 原话 "Use 0.3.1 on anything older"）；本机已装 **v0.6.2**，与 seitanism 的 MultiRef fork **同名 4 节点撞车**（装前必做「装第三方节点包前：同名节点撞车体检」）|
| `H3SigmaRefiner` | `yichengup/ComfyUI-YCNodes-MiniMax-H3`（`py/h3_sigma_refiner.py`）| 未进 Manager 注册表 |
| `MmuuaiGroupBypass` | `mmuuai/mmuuai-group-bypass` | 同一作者另有 `mmuuai-resolution-selector` |
| `AudioCrop` | `christian-byrne/audio-separation-nodes-comfyui` | |
| `AudioInfoNode` | `SayanoAI/Comfy-RVC`（`custom_nodes/audio_nodes.py`）| ⚠️ 本机装的是 **AIFSH/ComfyUI-RVC**（另一个 fork，无此节点）；再装 SayanoAI 版会**重复注册 `LoadAudio` 等节点名** |
| `VRGDG_MiniMaxH3AudioDrive` | `vrgamegirl19/comfyui-vrgamedevgirl` | UP 自己的 `swan7-py/ComfyUI_Swan_Bits` 提供**改名版** `SWAN_MiniMaxH3AudioDrive` / `SWAN_AudioInfo`（免装重依赖），但**节点名不同 → 工作流要改名** |

**反查节点出处的最快权威源**（注册表搜不到时）：ComfyUI-Manager 的 `extension-node-map.json`（`https://raw.githubusercontent.com/Comfy-Org/ComfyUI-Manager/main/extension-node-map.json`，约 5600 条，`{repo: [[节点类名…], …]}`）——一次下载本地反查全部缺件，比逐个 web 搜准。**注册表没有 ≠ 不存在**（UP 自制/个人插件不在册，需去 GitHub repo 搜或问 UP 网盘包）。

**2026-09-11 本机部署实测结果（Windows / 5080 16G）**：
- 升级路径：`git -c http.proxy=http://127.0.0.1:7897 fetch --depth 1 origin master` → `git reset --hard FETCH_HEAD`（Clash Verge 端口 **7897**，不是 v2rayN 的 10808；代理不通时 `curl` 走直连 api.github.com 反而能通，但 `git` 必须代理）→ `uv pip install -r requirements.txt`。0.30.2 → **0.35.0** 后 **现有插件 IMPORT FAILED = 0**（SolAttn/TE-Speed 也没炸，但 TE-Speed 的 `comfy/ldm/minimax/model.py` 补丁被 reset 覆盖，`.bak` 保留）。
- ⚠️ **杀 ComfyUI 必须杀 python 子进程**：`process(kill)` 或 taskkill 杀 bash 外壳后，`main.py` 的 python 仍在跑并占端口，会出现"新实例启动但节点没变"的假象。用 `powershell Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? CommandLine -like '*main.py*' | % { taskkill /F /PID $_.ProcessId }`。
- ⚠️ 本机 bash **MSYS 路径转换已关闭**：`taskkill //F` 会报 Invalid argument，要用 `/F`；`bc` 不存在，算 GB 用 python。
- ⚠️ **原生程序（`curl` / `pip` / `uv` / `stat`）不认 `/d/...` 路径**：`curl -o /d/x/y.gguf` 会以 `curl: (23) client returned ERROR on write` **写 0 字节就退出**（脚本若只看 exit code / 目录存在，会当"下完了"）→ **对原生程序一律给 `D:/x/y.gguf` 形式**；bash 内建（`mkdir`/`ls`/`find`）仍用 `/d/...`。2026-09-14 因此白下两轮（后台 20GB 任务一起空转）。
- ⚠️ **uv 建的 `.venv` 没有 pip**（`python -m pip` → `No module named pip`）→ 装包用 `uv pip install --python "D:/<ComfyUI>/.venv/Scripts/python.exe" <wheel>`；`.venv` 的 Python 版本决定 wheel 的 `cp3XX`（本机 3.12.11 → `cp312`）；**`--no-deps` 后要自己补作者声明的运行时依赖**（llama_cpp 漏了 `diskcache`）；**uv 拒绝改名后的 wheel**（`The wheel filename … is invalid: Must have a version`）→ 存盘就用原生全名。**超长 inline 命令/heredoc 会被 hardline 拦**，且 heredoc 会吃掉反斜杠 → 一律先 `write_file` 写 `.sh`/`.py` 再跑。以上 5 条完整版 + 下载脚本模板 + 代理分工表：`references/windows-local-env-install.md`
- **AudioInfoNode 是死结**：节点名唯一来源 `SayanoAI/Comfy-RVC`，但其 `__init__.py` 无条件加载 STT(spacy)+UVR(audio_separator/demucs)+RVC训练链(fairseq/torchcrepe/faiss)，`monotonic_align` Windows 还要编译；且与本机 AIFSH/ComfyUI-RVC 撞节点名。**正解 = UP 自己的 `ComfyUI_Swan_Bits`（swan7-py，2 文件 0 依赖）**：`AudioInfoNode`→`SWAN_AudioInfo`（4处改：type / S&R名 / 输出槽重排 / 连线 origin_slot 2→1 / widgets=[fps]），`VRGDG_MiniMaxH3AudioDrive`→`SWAN_MiniMaxH3AudioDrive`（签名完全一致，无损）。装不起来的包移去 `_disabled_plugins/` 而非删除。
- 模型源：融合版 HF `smhfacct/...hybrid-models`；nvfp4 编码器 `Comfy-Org/MiniMax-H3`；video VAE int8 走第三方 `GuangyuanSD`；turbo resized LoRA 走 `Kijai/MiniMax-H3_comfy`；**Combat LoRA 的 CivitAI 版无 API key 时用 HF 镜像 `JOKER141/MiniMax-H3-Combat-Base-V2`（H3_Combat_V2.safetensors，155MB，同尺寸）**。国内一律用 `hf-mirror.com`。

### 工作流 JSON 连线体检（API 格式，2026-09-10 实测）

凡哥给工作流 json 问"连线有没有问题"（改名节点组、换掉 API 节点、删插件后的收尾），**不要靠眼看截图**——工作流 json 是 API 格式（顶层键 = 节点 id，`inputs` 里 `[node_id, out_idx]` = 连线），程序化体检最快：

```bash
<venv>/bin/python scripts/audit_workflow_json.py <工作流>.json [另一个].json
```

体检输出三类结论：
- **无效引用**（输入指向文件里不存在的节点）= 一定错，节点被删或手工改断
- **悬空输出**（输出没人用）= **只是候选，绝不能直接判死**（见下条铁律）
- 子图节点（`1297:123` 形式）在顶层键里出现属正常

⚠️ **判"没用"的铁律（凡哥当场纠正，2026-09-10）：引用统计只能筛候选，判死必须以「参考版本的设计意图」为依据。**

只看"谁引用谁"会**系统性误杀"没接完的开关节点"**——它们的输出悬空不是因为冗余，而是因为**漏连**。凡哥原话：『没有用的可以删，但一定是有依据的删，不要瞎试』『充分理解参考工作流每一根线的意图再改』『不知道的不要猜，没地方查就说不知道』。

正确流程：
1. 拿**参考版本**（UP 原始版 / 改动前版本，如本例的 V3）比对同名节点**本该接什么**
2. **成对/备用结构最容易被误杀**：先查**参考版怎么接的**再下结论——参考版里第二条链可能本来就是 **bypass 的备用件**（V4 实例：`1335` mode=4 + 无下游 = 设计如此，不是漏接；二采与一采**共用 `1299`**）；也可能确实漏接。差异只能靠参考版判定，不能凭"看起来像成对结构"推断。
3. 同一现象在不同**参考版本**下结论相反 → **参考版才是判据**。凡哥原话：『我们不要超越，我们要和标准版完全对齐，不要增加不要减少』——允许的差异只有他点名的那一处（本例＝API 提示词节点换成本地提示词组）。
   ⚠️ 我曾按"一采一套、二采一套 LoRA"推断，把 `1329/1341.model` 从 `1299` 改接 `1335`，并新增一个音频 `Any Switch`（二采音频优先）——**全部被标准版 `V4-2` 推翻**：标准版是 `1335` **bypass 的备用链**、`1318`(二采音频) 同样悬空、不新增任何节点。推断与参考版冲突时主动翻案，并以参考版为准，同时说清哪句是推断。
4. 对齐参考版的正确做法：**以参考版为底稿重建**（删被替换的那个节点 → 迁入替代节点组 → 按参考版重建连线 → 重新分组布局），**不要在自己改过的版本上打补丁**——补丁会累积偏差，且分不清"设计差异"与"我的猜测"。交付前把"与参考版的差异清单"逐条列给凡哥（只应剩他点名那一处）。
5. 真判定冗余才删；**删完必须重跑一致性校验**（无效引用/悬空输入都=0）

**改法比结论更重要**：报告不只列"哪些悬空"，要给出"接到哪里 / 怎么接"的可执行方案，并让凡哥先确认设计意图（他对 UP 的开关设计比引用统计可信）。

实例（V4 换掉 API 提示词节点后）：本地链 `QwenTE_ModelLoader → QwenTE_ImageInfer → ShowText → MiniMaxH3UnifiedToVideo.prompt` 已通，但 `Any Switch → ShowText` 那条"本地 vs 原始提示词回退"支线**只接到显示、没接进采样器**=回退功能是摆设；另有重复的 `LoraLoaderModelOnly`（1299 已是同 LoRA 且被用）和 `VAEDecodeAudio` 悬空。**报告要给\"改法\"不只给\"问题\"**：回退支线要么改接 `prompt`，要么删掉两个节点。

#### `Any Switch (rgthree)` 语义（多模式提示词组的关键坑）

`Any Switch` = **取第一个非空**输入，没有 index 旋钮。所以 UP 工作流里 T2VA/I2VA/L2VA/FL2VA/Ref2VA 五个 `PrimitiveStringMultiline` 同时有内容时，**永远只走 any_01**——"模式切换"实际靠 **Ctrl+M 静音**掉不需要的那几个（被 mute 的节点不会进 API 格式）。凡哥问"为什么系统提示词不生效"先查这里，是用法不是连线错。

#### 换节点组前的验证纪律

报"该输入是否合法"之前先看**插件源码**，别按 V3 原版推断：V3 的 `QwenTE_ImageInfer` 只接 1 张图，V4 接了 `图片/图片2/图片3`——多图输入是否支持决定"能用"还是"执行即报错"，云端一条 `grep -rn "图片2\|图片3" <插件目录>/*.py` 就能定论。

## 工作流 UI 格式编辑（节点组 / 改连线 / 重排布局）

**先判格式，别白干**：两种 json 长得完全不同——

| 格式 | 顶层键 | 能干什么 |
|---|---|---|
| **API 格式** | 扁平节点 id（`"201": {...}`），只有 `class_type`/`inputs`/`_meta` | 只能程序化体检连线；**没有坐标、没有 groups → 做不了节点组** |
| **UI 格式** | `nodes` / `links` / `groups` / `definitions` / `last_node_id` / `last_link_id` | 全部：改坐标、建组、改连线、加节点 |

凡哥要"把节点分类分组、摆整齐"时：**先确认文件是 UI 格式**；是 API 格式就请他 UI 里 `Workflow → Export` 导出（一步 30 秒），别硬造 UI 文件（widgets_values 顺序错=丢参数、行为被改）。

**UI 格式结构要点**（改之前必须知道）：
- 连线元组：`[link_id, 源节点id, 源输出槽, 目标节点id, 目标输入槽, 类型]`
- **改一根线要同时动三处**：`links` 数组 + 源节点 `outputs[槽].links` 列表 + 目标节点 `inputs[项].link`。只改一处 → 加载后连线错乱
- 目标输入槽 = `inputs` 数组下标（不是名字），先 `next(i for i,it in enumerate(...) if it["name"]==...)` 定位
- 新增节点：**复制同类节点的完整结构**（含 `properties` 里的插件 id/版本），改 `id`/`pos`/`size`/`title`/`inputs[].link`/`outputs[].links`，`last_node_id`+1；新 link id 从 `last_link_id`+1 起
- `outputs[槽]["links"]` 可能是 `None`（不是空列表）——写入前要判类型，`setdefault` 救不了 None
- 旧文件常带**坏链接**（指向已删节点的 link），清理时同步从源 `outputs[].links` 摘掉

**分组 + 布局配方**（本次实做，可直接复用）：
1. 按**数据流分区**（素材 → 提示词 → 模型加载 → 一采 → 放大链 → 解码输出），一组一列；把"开关/兜底"类节点放进它服务的功能区，**不要单独隔离成"待删区"**（那等于提前判死，见上文铁律）
2. 每组：`列宽 = max(成员宽)`；组内竖排累加 `y += 高 + GAP_Y`；节点 `pos = [组x + PAD, 当前y]`；组框 `bounding = [组x, TOP_Y, 列宽+2*PAD, 内容高]`；`x += 列宽 + 2*PAD + GAP_X`
3. 组对象字段：`{"title","bounding","color","font_size","flags"}`（颜色分组、字号 28 可读性好）
4. **交付前生成 HTML 预览**（把组框+节点按同比例画成 div）在聊天里 `::preview` 给凡哥看——他确认后才导入；比让他先导入再改省一轮
5. 布局只改 `pos`，**不要动 links/widgets_values**

一致性自检（改完必跑）：`scripts/audit_workflow_ui_json.py <文件>.json` —— 校验格式、坏链接、inputs↔links 双向一致性、节点是否漏入组。

## 0.35 官方核心节点 vs 社区节点：参数表迁移（2026-09-10 实测）

0.35 把一批社区能力并入核心（`BlockSparseAttention`＝显示名 Model Sparse Attention、Comfy Compiler 等）：**同名节点、参数表不同**。加载社区版保存的工作流 → 校验报一串"值非法"→ **整条 prompt 秒退**：

```
- Value not in list: sink_conditioning: 256 not in ['exact_kv','exact_kv_and_rows','off']
- Value 1.3 bigger than max of 1.0: start_percent
- Value 12288 bigger than max of 256: extra_tokens
- Failed to convert an input value to a INT value: min_tokens, , invalid literal for int() with base 10: ''
```

**判定**：报错的"参数名↔值"**整体错位一格** = 参数表变了（社区版 `selection` 存的是显示名 `"Sol-Attn (adaptive tau)"`，官方 options 是 `["sol-attn","sla","vsa"]` → DynamicCombo 解析失败 → 后续 widget 值按错位置解读）。**不要逐条试值**。

**修法**：① 读**云端**节点源码拿合法取值（`sed -n '/class <节点名>/,/^class /p' <文件> | head -95`，官方核心节点在 `comfy_extras/`）；② 按官方 input 顺序重写 `widgets_values`，判断不了语义就**全落官方默认值**；③ 节点在子图里时改 `definitions.subgraphs[*].nodes`；④ 改完逐项校验区间/枚举+重跑一致性自检。参数表、完整报错、通用信号见 `references/035-node-migration.md`。

**依赖同类坑一**：`llama_cpp` 报 `GLIBCXX_3.4.30 not found` **≠ 没装**，是 conda base 的 libstdc++ 太旧（GCC 11 → 只到 3.4.29）。**GLIBCXX↔GCC 对照**：3.4.29≈GCC11 / 3.4.30≈GCC12 / **3.4.32≈GCC13** / 3.4.35~36≈GCC15~16——报错要几号 = 对方是哪个 GCC 编的，据此选库。两条路：① 只要 ≤3.4.30：`ln -sf /usr/lib/x86_64-linux-gnu/libstdc++.so.6 /root/miniconda3/lib/libstdc++.so.6`（Ubuntu 22.04 系统库到 3.4.30）；② 要求 **≥3.4.32**（系统库不够）→ 换 conda-forge 新版，**改完必须重启 ComfyUI**。

⚠️ **`libstdcxx-ng` 是空壳包 —— 装它等于没装（2026-09-10 实测更正，本条曾建议装它，是错的）**：
- 实证：下载 conda-forge 的 `libstdcxx-ng-16.2.0-*.tar.bz2` → **1545 字节、零文件**；`conda search --info` 显示它 `dependencies: libstdcxx 16.2.0`——它是只声明依赖的 meta 包，**真文件在 `libstdcxx`（不带 `-ng`）里**。
- 正确命令：**`conda install -y -c conda-forge libstdcxx`**（≥13 即可，15/16 也向下兼容），装完 `ls -la $PREFIX/lib/libstdc++*` 应出现 `libstdc++.so.6.0.xx` + `libstdc++.so.6` 软链。
- **最迷惑的症状**：`conda list` 显示升级成功、事务全绿，但 `$PREFIX/lib/libstdc++.so.6` **根本不存在** → 链接器回退系统库 → **报错路径从 `/root/miniconda3/bin/../lib/...` 变成 `/lib/x86_64-linux-gnu/...`（路径变化 = 加载源换了的铁证，别当成新问题）**。
- **别加 `--no-deps`**：本想\"避免连锁变更\"，结果正好拦掉实体包 `libstdcxx` → 零文件（本次踩坑根因）。
- 判包是不是空壳（通用手法）：`curl -sL -o /tmp/p.tar.bz2 https://conda.anaconda.org/conda-forge/linux-64/<包名-版本-build>.tar.bz2 && ls -la /tmp/p.tar.bz2 && tar -tjf /tmp/p.tar.bz2 | head`——体积异常小/列表空 = meta 包。

**依赖同类坑二（本坑修好后立刻会撞上的下一层）**：`comfyUI-llama-TE` 跑起来后报 `RuntimeError: 当前 llama-cpp-python 不支持 Qwen35ChatHandler，请更新 llama-cpp-python。`（`nodes.py` 的 `_创建qwen35聊天处理器`）→ **PyPI 的 `llama-cpp-python`（abetlen 原版）压根不支持 Qwen3.5+**：官方 issue #2137「Support for Qwen 3.5 models」已关闭，社区结论是改用 **JamePeng fork**。装它家的预编译 wheel（Linux 只有 `cu131 / cu128 / cu126 / cu124`，**没有 cu130-linux**；Windows 才有 cu130——按\"torch 是 cu130\"去拼 `-cu130-linux` 会 404），文件名形如 `llama_cpp_python-0.3.49+cu131-cp312-cp312-linux_x86_64.whl`。选版顺序：cu131（最接近 cu130）→ 失败退 cu128。**tag 与 asset 文件名一律用 GitHub API 抄**（`curl -s "https://api.github.com/repos/<owner>/<repo>/releases?per_page=40"` 打印 `browser_download_url` 复制粘贴，别手打）——手打连字符/大小版本号极易错（本次把 `cu131` 打成 `cu130` → 404 白跑一轮）；装前先 `pip uninstall -y llama-cpp-python`，装完**验 handler 列表**而不是看 pip 输出（`llama_chat_format` 里要有 `Qwen35ChatHandler`）。

**依赖同类坑三（第三层）**：模型链上的 `MiniMaxH3MemoryEfficientSageAttentionPatch`（KJNodes）报 `sageattention is not new enough version or could not determine CUDA architecture` → 该节点在**模块导入期**探针 `sageattention.core` 的 **6 个符号**（`per_thread_int8_triton` / `per_warp_int8_cuda` / `per_block_int8_triton` / `per_channel_fp8` / `get_cuda_arch_versions` / `attn_false`），任一步失败就**静默留 `None`**、跑图时才炸。版本事实：PyPI 最高 **1.0.6**（只有 `attn_false`）、thu-ml **v2.2.0 tag 也只有 `get_cuda_arch_versions`**、**main 才 6 个全有** → 要的是 main 级 API。

⚠️ **作者的预编译 wheel 在 torch ≥2.13 上装不了（2026-09-10 实测，别再试）**：`huggingface.co/Kijai/PrecompiledWheels` 的 `sageattention-2.2.0-cp312-cp312-linux_x86_64.whl`（2025-07 编）导入即 `undefined symbol: c10::impl::cow::materialize_cow_storage`。该符号 **PyTorch 2.13 起官方移除**（release notes #179063：COW 改为 pluggable materializer hook）→ **永久 ABI 不兼容**，换 libstdc++ / 改配置都救不了；**换 libstdc++ 后再报这个符号 ≠ 修错了，是进到下一层了**。旁证：`woct0rdho/SageAttention` 只发 Windows wheel（无 Linux）；thu-ml 仓库搜 torch 2.13/2.14 issue = **0 命中**（上游尚未适配）。结论：**Linux 版必须按 torch 版本逐个排查 —— “查不全”不等于“没有可用版本”**（2026-09-10 二次查证更正：此前“暂不存在成品”那句下早了）。已知 sageattention Linux wheel 源：
- **`pixeloven/SageAttention-Wheels`**（2026-08-19）：`sageattention-2.2.0+cu130.torch2.13.0.sm120-cp312-cp312-linux_x86_64.whl` —— 按 sm80/86/89/90/**120** 分文件、附 `BUILD-INFO-<arch>.txt` 构建信息可查证。**它是 torch2.13 编的、本机是 2.14，兼容性未实测**，装完必须验 6 符号 + 真加载。
- `snw35/sageattention-wheel`：`+cu12 / +cu13` 的 linux whl（2026-01）。
- `kijai/PrecompiledWheels`：旧（torch ≤2.12，见上）。
- `woct0rdho/SageAttention`：ComfyUI 官方 docs 指定的源，但**只有 Windows**。

⚠️ **“为什么很多 UP 都在用这个节点” = 平台差异，不是“你环境特殊”**：现成 wheel（woct0rdho / kijai）主要面向 **Windows** 用户（ComfyUI 整合包主流）；Linux / 云端用户要另找编好的 linux 版本。凡哥会当场反问这句话 —— **必须先把 PyPI → GitHub releases → 官方 issue 评论区查全再下结论**，找不到才照实说，且**禁止把“手动提取 / 绕开安装器”当解法**。
找 wheel 的通用招式：GitHub 搜 `sageattention in:name sort:updated`，挑文件名同时含 `linux_x86_64` + 匹配的 `cu###` / `torch###` / `sm120` / `cp312`。——找不到就照实说，别把\"手动提取/绕开安装器\"当解法。

自编的两道坎（**当前源码编译堵死，别原地重试**）：① torch 的 `_check_cuda_version` **硬性要求 nvcc 的 CUDA major == torch 的 CUDA major**（12.8 vs 13.0 直接 raise，**无环境变量可跳**）→ 先装匹配 nvcc（Ubuntu 22.04 实测：NVIDIA keyring → `apt-get install -y --no-install-recommends cuda-nvcc-13-0 cuda-cudart-dev-13-0`，编译时 `CUDA_HOME=/usr/local/cuda-13.0`）；② nvcc 对上后 thu-ml main 仍编不过 torch 2.14：`'sizes' is not a member of 'at::symint'`（报在 `csrc/qattn/pybind_sm80.cpp` 引入的 torch 头里；setup.py 里这个编译单元对**任意架构**都会编，指定 `TORCH_CUDA_ARCH_LIST=12.0` 也躲不开）。

该节点性质（决定出路）：KJNodes 自述 `EXPERIMENTAL!`、作用只是**减峰值显存**、**可旁路**——ComfyUI 里选中按 **`Ctrl+B`**（旁路自动直通输入→输出，**无需改线**）；ComfyUI 官方 docs 的 H3 教程也说明它可由 `--use-sage-attention` 替代。旁路会失去显存优化（长视频有爆显存风险）且偏离标准版，**属需凡哥决策的事项，摆事实给选项、别自己替他绕**。逐符号诊断命令、nvcc 安装、社区 issue 出处见 `references/torch-cuda-dependency-matrix.md`。

## 依赖链排障纪律（凡哥 2026-09-10 反复强调，违反必被当场质疑）

1. **先查现成件，最后才自己编译**：遇到\"某包版本不对\"，搜索顺序 = ① PyPI / GitHub releases 有没有匹配 wheel → ② **官方 issue / 作者仓库里有没有人贴出可用包**（本次 kijai 预编译包就是在 thu-ml issue #361 的评论区被点名的）→ ③ 才考虑源码编译。我这次先带凡哥装 CUDA toolkit + 编译，白绕一大圈，被当场纠正。
2. **出问题去找官方解法，不许\"绕开\"**：凡哥原话『出现问题就去找官方相应的解决方案，不要说绕开就绕开，你不知道就去查，别瞎试』。把\"手动提取包 / 绕过安装器\"当解法 = 逃避根因；正确动作是查清\"为什么装不上\"（本次靠\"下载官方包、发现它只有 1545 字节\"定位根因）。
3. **汇报必须证据分级**：凡哥原话『你确定你现在不是在瞎试瞎猜吗？都是有依据的吗？』→ 分三档写：🟢 **硬证据**（凡哥机上的实测输出 / 官方原文或源码 / API 实测）｜🟡 **推断**（写明推断链 + 未验证点）｜🔴 **未验证**（明确列出）。不确定就写\"不知道\"，**禁止把推断当事实**、禁止把第三方传闻当官方。
4. **一轮只给一条命令**：凡哥会把你给的\"备选命令\"一起跑（本次 cu131 / cu128 两条都跑，环境状态一度不明）。给命令时明确写\"**只跑这一条**\"，备选方案留在文字里、等结果再发；命令要自带校验步骤（每步有独立输出，便于定位）。
5. **版本号一律抄，不手打**：tag / asset 文件名 / build 串用 `curl -s https://api.github.com/...` 或 `conda search --info` 原样复制（手打 `cu131` 打成 `cu130` 直接 404、白跑一轮）。
6. **命令前先自问**：这条命令依据是哪来的？官方文档 / 源码 / 本人实测 / 社区实践？社区实践要**明说\"我没在你的机器上实测\"**。

## 装第三方节点包前：同名节点撞车体检（2026-09-14 新增，必做）

**同名节点跨包注册 = 后加载的覆盖先加载的 → 已存工作流参数整体错位 / 校验失败**（与「0.35 官方 vs 社区同名节点」同一类故障，只是这次发生在两个第三方包之间）。装任何 H3 / LTX 系第三方包前先跑：

```bash
python scripts/audit_node_pack_collision.py <新包目录> <已装包目录>
python scripts/audit_node_pack_collision.py <包A> <包B> --class <冲突类名>   # 并排对比参数表
```

**实例（2026-09-14 本机）**：`seitanism/ComfyUI-H3-Motion-Context-MultiRef`（fork）与本机 `NikoDemon80/ComfyUI-H3-Motion-Context` **v0.6.2** 注册 **4 个完全同名**节点（`MiniMaxH3MotionContext` `/Trim` `/SaveLatent` `/LoadLatent`），且参数表是两代东西：

| | NikoDemon80 v0.6.2（本机） | MultiRef fork |
|---|---|---|
| `context_length` | 枚举 `22/5/39/56`，默认 22 | 自由 INT，默认 39 |
| `encode_mode` / `anchor_mode` / `crop` / `audio_mode` | 无 | 有 |
| `context_frames` | optional | required |

**判死/放行的关键是「引用」，不是名字**（和下面工作流体检同一条铁律）：
1. `grep -rl "<冲突类名>" <ComfyUI>/user/default/workflows/` —— 已存工作流有没有用到（本例命中 `H3长视频MV_context_lightx2v_长视频.json`）
2. grep **新工作流 JSON** 用不用同名节点（本例 `NEW - Music Video.json` **0 引用** → 撞车不致命，只是两包仍互相覆盖）

三条路，**摆给凡哥拍板，别自己删包**：

| | 做法 | 代价 |
|---|---|---|
| ① 停用旧包（首选） | 旧包移去 `_disabled_plugins/`（**移不删**，一条命令切回） | 引用旧包节点的工作流暂时不可用 |
| ② 改名共存 | 改 fork 侧冲突类名（连带改内部 import / 继承引用） | 改第三方源码，以后 `git pull` 覆盖、需重打补丁 |
| ③ 换别家 | 弃用该包，选无同名节点的替代实现 | 功能可能不如它全（如母带整轨保护） |

**凡哥偏好（本类任务）**：这件事他要的是「**直接找做好的工作流拖进 ComfyUI**」，**不要自研节点图**；节点存废 / 包切换必须他拍板（SOUL 铁律：先查设计意图 + 引用再定，禁止自作主张删）。

### 选包前：先核「最新」，再判「同代」（2026-09-14 凡哥纠正，必做）

凡哥问「最新的 X 工作流」时，**禁止凭搜索快照 + 包自己的 README 下结论**。本次就因此把 `MultiRef`（最后推送 **9-05**）说成「最新的 MV 工作流」，被当场追问『**你确定找的这个工作流是最新的吗？**』——一拉时间排序就发现 9-06 之后还有好几个更新的，而且 MultiRef 恰是**唯一有同名撞车**的那个。**「星最多 / 功能最全」≠ 最新。**

核验 = **时间排序**，不是关键词命中：

```bash
P=http://127.0.0.1:7897
# ① 单仓库实时状态（pushed_at = 最后一次推送，不是 created_at）
curl -s -x $P "https://api.github.com/repos/<owner>/<repo>" \
 | python -c "import sys,json;d=json.load(sys.stdin);print(d['pushed_at'],d['stargazers_count'],d.get('description'))"
# ② 全站按最近推送排序（找有没有更新的实现）
curl -s -x $P "https://api.github.com/search/repositories?q=<关键词>&sort=updated&order=desc&per_page=20" \
 | python -c "import sys,json;[print(r['pushed_at'][:10],r['stargazers_count'],r['full_name'],'|',(r.get('description') or '')[:70]) for r in json.load(sys.stdin)['items']]"
```

**多组关键词都要搜**（`minimax h3 music video` / `comfyui h3 mv` / `h3 music video workflow` / `H3 Continuum`）——单查询必漏；搜完把「更新的候选」逐个看 README 第一屏，别只看名字。

**「同名节点」≠「同一个包的版本」**：fork 与上游常是**分叉后各自演进的两条线**，同名节点可能停在**分叉那一代**。判定依据（三处源码/文档，别猜）：① `nodes.py` 首行有没有 `MODIFIED FORK NOTICE: <日期>`；② `MODIFICATIONS.md` 的 fork history 节；③ 上游 `CHANGELOG.md` 分叉点前后的版本记录。

实例（`MultiRef` vs `NikoDemon80` 原版）：分叉自 **2026-08-13**；fork 的 `MiniMaxH3MotionContext` 保留旧一代参数（含作者自标 legacy 的 `anchor_mode=before`、`encode_mode`、`audio_mode`、自由 `context_length`），而上游 **v0.6.2**（9-06）已把该节点精简重构（枚举 `22/5/39/56`、删掉上述模式开关、`context_frames` 改 optional）。**两条线都还在活跃更新、谁都不含谁** → 「装 fork 覆盖原版」**不等于升级**，是换一条线；节点存废仍按上一条铁律（查引用 + 凡哥拍板）。

候选包**批量分诊**（一次看清「谁零撞车 / 谁要下模型」）：把本机已注册类名池（遍历 `custom_nodes/*` + `comfy_extras/*` 收集，本次得 **815 个**）与每个候选包的 `NODE_CLASS_MAPPINGS` 求交集；成对深比参数表用 `scripts/audit_node_pack_collision.py`（本次只用它 + 交集就分出「MultiRef 撞 4 个 / 其余候选全部零撞车」，不必逐个装）。

### 顺带做：工作流要的模型 vs 本机已有（判「要不要下模型」）

从 UI 格式工作流抽加载器节点的 `widgets_values[0]`，对本地模型目录逐个核 —— 这决定「装完能不能直接跑」：

```python
import json
w = json.load(open(WORKFLOW, encoding="utf-8"))
for n in w["nodes"]:
    if n["type"] in ("UNETLoader", "CLIPLoader", "VAELoader", "LoraLoaderModelOnly"):
        print(n["type"], n.get("widgets_values", [""])[0])
```

⚠️ **加速 LoRA 的文件名最容易不匹配**（实例：工作流写 `8step_v1.0`，本机只有 `lightx2v_turbo_4step_v0.1`）→ 属「节点里换一下文件名 + 采样步数跟着调」的小改，**不是缺模型，别去下载**。其余四件套（H3 主模型 / Qwen3-VL 编码器 / 视频 VAE / 音频 VAE）本机已齐。

⚠️ **上面这段只扫「加载器类节点」的写法会漏件（2026-09-15 踩过，被凡哥当场发现）**：模型名还会出现在**任意节点的 optional 输入**里。实例 `taeh3.safetensors`（TAE 轻量预览解码器，9,791,388 字节，HF `GuangyuanSD/minimax_h3_video_vae_int8_convrot` → `models/vae_approx/`）是 `ModelPreviewOverrideKJ` 的**可选输入** `tiny_vae`，工作流里填的是它而非 `none` → **必需**，但只扫 loader 节点的脚本查不到，于是给出「10 处引用全就位」的**错误结论**。
**正确做法**：同时扫 `widgets_values_named`（按名）与 `widgets_values`（按位）+ 子图节点，判「必需 / 可选」看**那一格的实际取值**（`none`/空 才是真可选），不是看节点类别。验收口径 = `引用 N 个模型 / 缺 0 个`。

## 工作流缺件体检：权威源 = 运行实例的 `/object_info`（2026-09-14 本机实测）

补齐第三方工作流的节点时**别 grep 源码猜**——直接问正在跑的实例要全量已注册节点类，再对工作流的节点类型求差集：

```bash
# ① 端口可能不是默认 8188！先问进程要真实端口（本机实测跑在 18188）
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*main.py*' } | Select-Object -ExpandProperty CommandLine"
# ② 权威节点表（本机 3015 类）+ 实例身份（版本/torch/GPU/显存）
curl -s http://127.0.0.1:18188/object_info -o object_info.json
curl -s http://127.0.0.1:18188/system_stats
# ③ 该实例看得见哪些已存工作流（判断「他说放进去了」到底放哪了）
curl -s "http://127.0.0.1:18188/api/userdata?dir=workflows"
```

一键跑：`python scripts/audit_workflow_missing_nodes.py <工作流.json> [更多…] --models <ComfyUI>/models`

⚠️ **凡哥说「已经放进 ComfyUI 了」但 `workflows/` 里没有新文件时**：他很可能只是把文件**拖进了浏览器里的标签页**（未 Ctrl+S，服务端的 `/api/userdata` 就看不到）。别断言"你没放"——先扫全部安装（本机有 4 处 `comfyui*` 目录）、附件目录（`D:\Hermes\attachments\`）、Downloads/Desktop，再把"我找到的是哪份、名字对不对得上"摆给他确认。

### 四类「假缺件」必须排掉，否则报缺报假（本次全踩到）

| 假阳性 | 判定依据 |
|---|---|
| **前端节点**：`Fast Bypasser (rgthree)` / `Fast Groups Bypasser (rgthree)` | 只在 rgthree 的 **JS/TS** 里注册（`src_web/comfyui/fast_groups_bypasser.ts`），**永远不出现在 `/object_info`**。包已装即可，别报缺 |
| **子图实例**：`<uuid>` 形态的 type | 该 uuid = `definitions.subgraphs[].id`（本例 `d581531a-…` = 子图「模型加载」）。**子图内节点要单独收集**，别当缺件 |
| **加载器第 1 个 widget 不是文件名** | `CLIPLoader` = `[name, type]`、`UNETLoader` = `[name, weight_dtype]` → `minimax` / `default` 这类值会被当成模型名 |
| **模型匹配未归一化** | 工作流写 `MiniMax-H3\xxx.safetensors`，本机文件在 `diffusion_models/minimax_h3/xxx` → **按 basename 小写比对、忽略目录前缀**。不归一会把本机已有的模型误报成缺（本次第一版误报 4 个） |

### 装完新插件怎么验：不打扰在跑实例（`--quick-test-for-ci`，2026-09-14 实测）

补齐插件后要确认能加载，但**别为了验证就去重启凡哥正在用的实例**。ComfyUI 自带「只加载节点就退出」的模式：

```bash
cd <ComfyUI> && ./.venv/Scripts/python.exe main.py --quick-test-for-ci > ci_test.log 2>&1
echo "退出码=$?"; grep -c "IMPORT FAILED" ci_test.log
grep -iE "<新插件目录名>" ci_test.log        # 确认被扫到 + 各插件加载耗时
```

判断口径：`IMPORT FAILED` 计数为 0 = 全部注册成功；**每个插件会打印一行 `X.X seconds: <路径>`**，把新装的几个目录名 grep 出来就能证明它被扫到了（比只看总计数可信）。这条不占端口、不加载模型，可在实例运行时安全执行。

⚠️ **单条 `Cannot import name 'xxx' from 'cv2.ximgproc'` 之类的子功能告警 ≠ 包挂了**：LayerStyle 会报 `guidedFilter`（官方 issue #5），但只要**目标节点不在那个模块里就不受影响**——本例 `LayerUtility: NumberCalculatorV2` 在 `py/data_nodes.py`，只 `import torch` + `from .imagefunc import ...`，与 ximgproc 无关。**判影响面要打开目标节点所在文件看它的 import，别按包级告警下结论。**

### 提交 `/prompt` 成功 ≠ 输入值合法（2026-09-14 实测）

`Value not in list` **只在部分节点类型上触发**。本机实测：`VAELoader` 传一个根本不存在的模型名 `DOES_NOT_EXIST_ABC.safetensors` → **返回 200 并正常入队**（无 `node_errors`）；而 `DynamicCombo`（如 `sink_conditioning`）会拦。推论与纪律：

- **不要拿「提交后没报错」当「值合法」的证据**——文件真不存在会在执行期才炸。
- **跨平台工作流里的大小写/分隔符差异不必改**：工作流写 `MiniMax-H3\xxx`（大写）而下拉列表是 `minimax-h3\xxx`，或写 `Qwen/xxx`（正斜杠）而列表是 `Qwen\xxx` —— 校验放行，且 Windows 文件层不区分大小写、正反斜杠皆认，执行期能解析到文件。凡哥定了「不改工作流」时，**先实测再决定要不要动它**，别看到「字符串不在下拉列表里」就去改工作流。
  ⚠️ 本条是**校验层 + 文件解析语义**的实测；**端到端跑通属未实测**（本次未让他跑完整工作流），别把它说成「已验证能出片」。
  🔴 **2026-09-15 更正（真跑时被拦）**：同一类大小写差异，在**一采链路上的 `VAELoader`** 上提交即被拒 ——
  `value_not_in_list: vae_name: 'MiniMax-H3\minimax_h3_audio_vae_fp32.safetensors' not in ['minimax-h3\…']`。
  区别不在「哪种节点类型会校验」，而在**该目录在磁盘上的真实名字**（本例 `vae/` 实际叫 `minimax-h3`，
  `diffusion_models/` 实际就叫 `MiniMax-H3` 所以不报错）。**结论：无头提交前一律对组合框输入做
  case/斜杠归一化**（`scripts/ui2api.py` 的 `norm_combo` 会自动做），别指望 Windows 的不区分大小写救校验层。
- 探针必须带**输出节点**，否则校验提前返回 `prompt_no_outputs`（`node_errors` 空 → 什么也验不到）。用 `scripts/probe_combo_value.py <class_type> <输入名> <值>`。
- 被测节点若不接任何输出，ComfyUI 会把它**剪枝**（只校验不执行）→ 正好当纯校验探针；探完仍要 `POST /interrupt` + `POST /free` 收尾。

### 同名工作流 ≠ 同一份内容（本次教训）

`H3长视频MV_….json` 在**聊天附件**里 69,760B、在 ComfyUI `workflows/` 里 88,010B —— 名字一样、**节点清单不同**（附件版有 `AudioInfoNode`，ComfyUI 存过那份已换成 `SWAN_AudioInfo`）。**体检结论前后对不上时先比 size/hash**，别怀疑脚本。

### 本机环境 ≠ 云端标准版时：改环境，不改工作流（凡哥 2026-09-14 铁律）

凡哥原话：『**以我们在云电脑上跑通的那一版做最终版，不要改任何的**，我就要云电脑上跑通的那一版』。此前在本机做过的适配（`AudioInfoNode`→`SWAN_AudioInfo`、把 LoRA/主模型文件名换成本机有的）**一律作废**。正确姿势：

1. **装插件**补齐缺的节点（不换名、不旁路、不用"改名版"替代）
2. **造目录名**让工作流里的模型路径原样命中 —— 工作流写 `MiniMax-H3\xxx`，就在 `diffusion_models/`、`text_encoders/`、`vae/` 各建 `MiniMax-H3/` 子目录并**硬链接**现有文件 —— **用 `ln`（硬链接），不要用 `ln -s`**：Windows 上 MSYS 的符号链接常需管理员 / 开发者模式，硬链接在同一 NTFS 盘上普通权限即可，且**零额外空间**（本次给 20.9GB 主模型造别名目录 = 零拷贝）。
  验法（**建完必验，别只看命令没报错**）：`stat -c%h <链接文件>` 应为 **2**（>1 才是真硬链接，不是被复制成的副本）；`stat -c%s` 与源文件字节必须完全一致。
  落位三处（本例）：`diffusion_models/` `text_encoders/` `vae/`；已存在的（如 `vae/MiniMax-H3/minimax_h3_audio_vae_fp32.safetensors`）跳过即可。
3. **下缺的模型**（真缺才下；**名字差一个字也算缺**，不许拿近似量化版顶）
4. 重启实例带上云端同款启动参数（本例 `--disable-cuda-malloc`，不带二采阶段会崩）。**重启前先 `curl -s http://127.0.0.1:<端口>/queue` 确认 `queue_running` / `queue_pending` 都为 0**（凡哥可能正在跑图）；**起实例用 `powershell -NoProfile -Command "Start-Process -FilePath '<bat 路径>' -WorkingDirectory '<ComfyUI 路径>'"`**（等价于他双击 bat，脱离本次会话）；起完轮询 `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<端口>/system_stats` 到 200 再报「已就绪」（本机实测约 15 秒）。本机启动脚本 = `D:\admin桌面\start_comfyui.bat`（内容就一行 `python main.py --listen 0.0.0.0 --port 18188`）——**改前先 `cp` 出 `.bak.<日期>`**，改完把 diff 亮给凡哥看；顺带确认脚本里没漏这个参数（本机原本就没带）。
5. 重跑缺件体检 → 目标 **0 缺** → 再请他开跑

凡哥对「对齐」的定义是**环境向标准版靠**，不是**工作流向本机靠**——反过来做必被打回。装重依赖插件（如为一个 `NumberCalculatorV2` 装 LayerStyle 173 节点）前**报代价给他，但默认照装**。

### 候选插件仓库取证（不装也能先对节点名）

`NODE_CLASS_MAPPINGS` **不一定是字面量**（ContextIR 是动态构建的 → 正则抓不到，会误判"这包没这些节点"）。兜底：clone 到暂存区后按**节点类名字符串**全仓搜：

```bash
git -c http.proxy=http://127.0.0.1:7897 clone --depth 1 <repo> <暂存目录>
grep -rhoE "['\"](MiniMaxH3|MinimaxH3|MMH3)[A-Za-z0-9_]*['\"]" <暂存目录> --include=*.py | tr -d "'\"" | sort -u
for t in <缺件节点名…>; do echo "$t -> $(grep -rl "$t" <暂存目录> --include=*.py | wc -l)"; done
```

本次靠这一招把 6 个缺件节点**一次性归到一个包**（`oufeixinxinren/ComfyUI-MiniMax-ContextIR`，含此前怀疑是「YCNodes 改名版」的 `MiniMaxH3TiledSampler` —— 它本就是该包的），省掉逐个 web 搜。云电脑那版（`5-MiniMaxH3-OPC交付版-1088P.json`）的完整缺件表、目录名对策、复现顺序见 `references/h3-opc-delivery-workflow.md`。

## 破坏性收尾与回答口径（凡哥 2026-09-14，本类任务通用纪律）

**① 凡哥说「把其余的模型删掉」时，先给分级清单再动手。** 删错一个模型，整套工作流立刻报「缺模型」跑不动。逐条列出：
- 🔴 **绝对保留** —— 工作流节点引用到的（文本编码器 / 视频+音频 VAE / LoRA / 放大模型 / 本地提示词 GGUF + mmproj），标注各自对应的工作流节点号
- 🟡 **取决于怎么换** —— 主模型位（工作流常有两个：融合版与省显存版），注明**哪个节点在用它**
- 🟢 **可安全删** —— 工作流 **0 引用**的，写明各多大、合计能省多少 GB

再给 A/B/C 选项（A＝只删 0 引用的那批，工作流毫发无伤…），**让他拍板，不替他决定删哪个**。同一条也适用于删生成资产 / 旧版本文件 / 做废的图。

**② 「换主模型」＝「改工作流」，必须显式点出矛盾。** 凡哥定过「云端跑通那版一个字不改」。他要换 UNET（如把融合版换成 Singularity）时：先说明**这会动工作流的加载器取值**，并问清换的是**哪一个**主模型位；两件事不能同时成立，摆给他选（只存着备用 / 换上去但承认这是动工作流）。

**③ 回答「是哪个模型」时只答他问的那个。** 顺手抛出的"另一个同名/类似的可选件"会让他误以为对不上 —— 本次他直接反问『那么说云电脑里的 comfyui 用的不是我说的融合模型？』，我回头解释了两轮。**附加信息必须显式标注「与当前问题无关」，否则不说。**

**④ 代理挂掉时走 hf-mirror，别擅自启他机器上的代理程序。** 诊断口径：国内站点 200 但 api 全 000 → 查代理进程（`clash-verge-service` 在跑而 GUI 没开 = 7897 端口死）。此时 **`hf-mirror.com` 直连可用**（实测首页 200，API 与 `resolve/main` 下载都通）→ 报告诊断 + 直接用镜像下；**不要**去启动 Clash Verge 或改代理设置（凡哥环境纪律：不擅启无关软件或改代理）。

## 无头提交：让 Agent 自己把工作流跑起来（2026-09-15 本机首跑成功）

凡哥问「**你可以控制本地的 comfyui 这个工作流了吗？你来自己跑吗？**」时，正确回答是「能」+ 当场给证据。前提是把 UI 格式工作流转成 API 格式提交：

```bash
cd <ComfyUI> && <venv>/python <skill>/scripts/ui2api.py <ui.json> api.json [--submit]
```

`POST /prompt` **只收 API 格式**（UI 格式直接 `HTTP 500`），而子图是**纯前端概念**、服务端不做转换 → 必须自己转。转换器干四件事：**子图拍平 / bypass 同类型直通重连 / 可达性剪枝 / 下拉值归一化**。

⚠️ **最容易漏、也最致命的是 bypass 直通**：`mode=4` 节点的输出可能直接喂关键链路（本例 `MiniMaxH3AudioLock.av_latent` → 一采采样器 `latent_image`），只删节点不重连 = 断链不出片。

⚠️ **提交后的 `node_errors` 是逐节点、逐参数名的精确报错**，拿它迭代：`value_not_in_list`（大小写，见上一节更正）、`required_input_missing`（本机节点比原文件多要求参数 → 去另一份工作流抄值，别猜）、`prompt_outputs_failed_validation`（总览）。提交前先 `POST /free`；跑起来后进度看日志（`user/comfyui_<端口>.log`）——第三方节点不上报进度，**界面没进度条 ≠ 卡死**。

**首跑成功的日志签名**：`Model MiniMaxH3 prepared for dynamic VRAM loading. 19995MB Staged` —— 20GB 级 int8 主模型在 **16GB 显存**上靠动态装载撑住了，**别预判「模型比显存大必 OOM」就劝退**。

完整配方、UI 格式的 4 类结构陷阱（顶层 links 是数组但子图 links 是字典、虚拟输入槽是负数 id、提升成子图输入的 widget 要用内节点 `widgets_values`）、`media_state` 条目结构与 `[input]` 后缀解析、以及**接手别人存的工作流必 diff 的 4 处**（本次 diff 出：两个 UNETLoader 指向已删模型 / 放大倍率 2.0 vs 1.5 / 少 2 个必需参数 / **5 条系统提示词被 Ctrl+M 全静音**）：`references/ui-to-api-headless-submission.md`

### 跑起来之后：崩溃会杀死任务线程；16G 上二采的实测边界（2026-09-15，四次尝试）

**① 二采在 16G 上「三种改法都没救回来」——别再重复这三条。**
症状签名（三次**完全一致**，都发生在**二采段重装 20GB 权重**时，此时一采早已正常出片）：
`aimdo: src/hostbuf-file-reader.c:92:ERROR:hostbuf_file_reader_read: device copy failed` → `aimdo memory compile error` → `torch.AcceleratorError: CUDA error: out of memory`

| 尝试 | 改动 | 结果 |
|---|---|---|
| 1 | 云版原设（`bypass_tiling=True` 不分块 / 缩放 1.5） | ❌ OOM |
| 2 | **`bypass_tiling=False` + `n_tiles=2` + `tile_overlap=16` + `refine_seams=True`** | ❌ **同样 OOM，分块没救回来** |
| 3 | 上述 + **摘掉 `MiniMaxH3MemoryEfficientSageAttentionPatch`**（按 aimdo+sage 已知 issue 的方向） | ❌ **同样 OOM** |
| 4 | 上述 + 缩放 1.5→1.25 | ⏸ 会话结束时**结果未知**（别引用为已成功） |

**✅ 已确认的规律（唯一该信的部分）**：同一套权重搬运机制下，**一采 960×544 三次全过、二采 1440×816 三次全崩**
→ 决定因素是**激活值规模**，不是「模型装不下」。因此：
- ❌ **别再**把二采 OOM 归因给 `bypass_tiling` 或 sage —— **两条都已在本机实测无效**（此前本 skill 写过「根因常常是 bypass_tiling」，那一版是**早下结论**，已作废）。
- ⏸ **未验证的剩余杠杆**（要用先按「一次只变一个变量」实测，别当结论转述）：继续降缩放（1.25→1.0）、缩短单镜时长（15s→9s，激活值约再降 40%）、启动加 **`--disable-dynamic-vram`**（关掉 `comfy_aimdo` 动态显存、退回经典离线调度；本机生效版本 = **`comfy_aimdo 0.5.3`**，另有 0.4.10 的 dist-info 残留）。
- 📐 **交付规格提醒**：OPC 交付版要 **1920×1088 = 960×544 × 2.0**，而连 1.5 都过不去 → **16G 机器很可能先天做不到交付分辨率的二采**，这不是调参问题。合理分工：**本机跑 960×544 一采做创作/审片/定稿 → 云电脑 32G 出 1088p 正式片**（OPC 交接包 + `examples/opc_client.py` 正是为此准备的）。

**② 崩溃后队列会永久卡在「排队=1」，必须重启 ComfyUI。**
CUDA OOM 会**打死 `prompt_worker` 线程**（日志 `Exception in thread Thread-N (prompt_worker)` → `soft_empty_cache` → `torch.cuda.synchronize` → CUDA OOM）；之后**再提交的 `got prompt` 也没人处理** → `/queue` 永远 `pending=1, running=0`。**CUDA 上下文已坏、热恢复不了**（`/free`、`/interrupt` 都救不回）。
监控看到「长时间 运行中=0 排队=1 且日志不增长」就是它，**别当成「还没轮到」**。
重启：`netstat -ano | grep <端口>` 取 PID → `powershell -NoProfile -Command "Stop-Process -Id <pid> -Force"`（⚠️ MSYS 里 `taskkill //F` 会被当成字面量 `//F` 报 Invalid argument）→ 本机命令行拉实例，约 50 秒就绪、队列自动清空。详见 `references/ui-to-api-headless-submission.md` §10。

**③ 16GB 机器的生产策略：一采先出片定稿（✅ 已验证）；「统一放大」尚未打通（⚠️ 别当已成立的能力）。**
首跑一采实测 **960×544 / 15.083s / 24fps / AAC 32kHz 双声道 / 3.8MB / ≈4.5 分钟** —— 这个分辨率审画面与口型已够，
**别每镜都硬扛二采**（每镜多 4~5 分钟且 16G 易炸）。
但**放大环节在 16G 上三次全崩**（见 ①）→ 目前完整可用的只有「**本机一采定稿 → 云电脑出 1088p**」这条路；
**放大跑通之前，不要向凡哥承诺本机能自产交付分辨率的成片**（他极在意「内部工艺测试通过 ≠ 商业发布」这条边界）。

## 附带脚本

- `scripts/ui2api.py` — **UI 格式 → API 格式转换器（+ `--submit` 直接无头提交）**。GUI 够不着又要真跑工作流时用它；bypass 直通、子图拍平、可达性剪枝、下拉归一化都内置。手改过 `OVERRIDES` 才能覆盖「widget 值损坏」与「节点代次不同」两类节点（脚本头部有说明）。
- `scripts/watch_prompt.py` — **盯任务的看门狗**（`<port> --comfyui <ComfyUI 目录> [--prompt-id <id>]`）：区分三种结局 —— **正常结束**（打印产物路径 + 实际字节）、**崩溃**（打印日志尾部，含 `CUDA`/`aimdo`/`prompt_worker` 标记）、**⚠️ 队列卡死**（`pending≥1` 但 `running=0` 且日志不增长 → 直接给出重启命令）。**别用「sleep 一段时间再 tail 日志」代替它**：卡死与「还在算」看起来一样（第三方节点不上报进度时日志本来就安静），看门狗靠「日志是否增长」区分，且卡死必须重启、等不来。
- `scripts/dl_model_resumable.sh` — **断点续传 + 逐字节校验 + 自动重试**的模型下载器（`<url> <目标D:/路径> <期望字节> "<名称>"`）。下任何 GB 级模型都用它，**别手写单发 curl**（单发版会在网络抖动时留半截文件就跳去下一个，只打一行 ⚠️ 就继续）。判「在跑还是死了」的两个信号见 `references/windows-local-env-install.md`。
- `scripts/audit_workflow_missing_nodes.py` — 工作流缺件体检（运行实例 `/object_info` 为权威源，自动排掉前端节点 / 子图 uuid / 加载器枚举值三类假阳性，模型按 basename 归一比对）。凡哥说"帮我补齐工作流节点"时**先跑它**，别手工拼命令。
- `scripts/audit_node_pack_collision.py` — 装第三方节点包前的同名节点撞车体检（跨包重名清单 + 参数表是否同代）。装 H3 / LTX 系插件前先跑它。
- `scripts/scan_missing_node_imports.py` — 扫描自定义节点目录，一次列出真正缺失的第三方模块（自动排除 ComfyUI 运行时虚报项）。装插件依赖 / 排查 IMPORT FAILED 前先跑它。
- `scripts/probe_combo_value.py` — **值会不会被拦**的实测探针（带输出节点，避开 `prompt_no_outputs` 白跑）。凡哥坚持「不改工作流」而值又看着不在下拉列表里时，先用它实测再决定；收尾自动 `interrupt` + `free`。
- `scripts/audit_workflow_json.py` — API 格式工作流 JSON 连线体检：列出无效引用与可疑悬空节点。凡哥问"连线有什么问题"时先跑它。
- `scripts/audit_workflow_ui_json.py` — **UI 格式**工作流校验/自检：判格式、坏链接、inputs↔links 双向一致性、节点漏入组。改完连线/重排布局后必跑。

## 详细实录

云端 Linux（RTX 5090）升级 + LTX-2.5 放大部署全程：`references/cloud-linux-upgrade-ltx25.md`
H3 生态模型来源/大小/公模库路径/放置目录总表（配 UP 工作流模型时先查它）：`references/h3-model-sourcing.md`
UP 小黄瓜 H3 全能生视频工作流（V3/V4）结构解剖——槽位索引、一采/二采双链、提示词组、开关语义：`references/up-h3-workflow-structure.md`
UI 格式工作流编辑实录（改连线/加节点/分组布局的完整配方与踩坑）：`references/comfyui-ui-format-editing.md`
0.35 官方核心节点参数迁移（`BlockSparseAttention` widget 整体错位）＋ `llama_cpp` 的 GLIBCXX 依赖修法：`references/035-node-migration.md`
torch/CUDA/libstdc++/wheel 的 ABI 依赖矩阵（GLIBCXX↔GCC 对照、`libstdcxx-ng` 空壳包、nvcc 必须同 major、sageattention × torch2.13 COW 符号移除）：`references/torch-cuda-dependency-matrix.md`
H3 / AI 音乐视频（MV）工作流版图——三条路线对比、**按 `pushed_at` 时间排序**的 9 个现成方案（含 2026-09-14 修正：MultiRef 并非最新且是唯一有撞车的，零撞名首选改为 `H3-Continuum 3.8` / `liaodaobin 数字人MV`）、`NEW - Music Video.json` 节点解剖、5 帧 preroll 与接缝 1s 重叠等对口型坑、教程链接核验手法、本机落地清单：`references/h3-mv-workflow-landscape.md`
**MV 制作「方法论」**（不是工作流版图，是"怎么做一个 MV"）——业界 5 步前置流程（**Treatment 先于 Storyboard**）、段落→视觉职能→镜头类型表、**镜数量级：传统 80-150 镜 vs H3 10-30 镜（一镜扛一个段落职能，"逐句配图"是错的）**、切镜铁律、参考图各司其职、AV 双栏分镜表 + Sync Points 产出物、齐白兰《爱的记忆》素材位置：`references/h3-mv-production-methodology.md`　（⛔ 凡哥 2026-09-15 定：**弃用自摸的 LTX 版 21 镜分镜**，改学现成方法论）
**云端跑通版工作流 + 本机复现对照表**（凡哥 2026-09-14 定最终版 = **`4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json`**，非 `5-…-OPC交付版-1088P`；两者节点集互差为空、只差放大倍率 1.5 vs 2.0，实测出过片的是 1.5×）——版本身份/规格/启动参数、**多份相似工作流的分辨判定法（节点集差 + widget 值）**、本机真缺 9 节点+2 模型实证表、三类假阳性、`MiniMax-H3/` 目录名对策、复现顺序、云端运维要点、同目录其它候选工作流缺件对照：`references/h3-opc-delivery-workflow.md`
本机 Windows 装环境/下模型的原生程序路径坑、uv venv 无 pip、wheel 选名与精确字节校验、llama_cpp(JamePeng) 正确装法+handler 验证、代理分工、`ComfyUI/models` junction 真相、收尾检查清单：`references/windows-local-env-install.md`
**把整套瘦身成「只跑一个工作流」**（凡哥 2026-09-15：「本机只跑这一个工作流，除了它用到的都删掉」）——官方 `.disabled` 停用机制、算所需包清单、**grep 与 `/object_info` 各漏一半所以两个都要跑**、复验两步、删前必重扫模型（含 optional 输入盲区）、硬链接双路径与磁盘收益口径、删除件留回源信息：`references/comfyui-workflow-pruning.md`
H3 音频路线与生成时长的**源码级**事实（media loader 的 `start/end` = 采样前裁剪源、`ReferenceSplitter.duration` 为 1-15 秒整数且本版=9、生成音频 latent 长度=时长且零初始化→**输出音轨由模型生成**、AudioLock 在本版 bypass、云端 API 限制 vs 本地限制**两套口径**、以及「整轨音频是条件还是只取前 N 秒」这个待实测问题）：`references/h3-audio-duration-and-limits.md`

**无头提交实操**（UI→API 转换器配方、子图/bypass/剪枝/归一化四步、`node_errors` 报错目录、UI 格式四类结构陷阱、`media_state` 条目结构与实体文件名对齐、接手别人工作流必 diff 的 4 处）：`references/ui-to-api-headless-submission.md`

⚠️ **写任何「上限/限制」前先分清是哪一层**（云端 API / 本地开源权重 / 模型本身 / 工作流节点参数）——2026-09-15 把云端 API 的「单次音频 ≤15 秒」当成 H3 通用限制写进文档，被凡哥**甩截图当场纠正**（本地 media loader 可载整首 2:30）。这类错误会直接改变方案骨架；**凡哥机器上看得见的东西，优先信他的截图**，别拿文档里的平台限制跟他争。同理：读源码得出的结论也要标明是「已确认」还是「待实测」，本次就发生过「音频不切只切画面」说过头、随后要自己收回的情况。
