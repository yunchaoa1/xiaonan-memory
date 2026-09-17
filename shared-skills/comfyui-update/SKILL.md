---
name: comfyui-update
description: 更新 ComfyUI 流程——D:\SDkecheng\ComfyUI、uv venv、RTX 5080、CUDA 13.0
---

# ComfyUI 更新技能

## 环境
- 路径：`D:\SDkecheng\ComfyUI`
- Python：uv .venv（CPython 3.12.11）
- GPU：RTX 5080 16GB，CUDA 13.0

## 更新流程

### 1. 拉取代码
```bash
cd /d/SDkecheng/ComfyUI
git init
git remote add origin https://github.com/comfyanonymous/ComfyUI.git
git fetch --depth 1 origin master
git reset --hard FETCH_HEAD
```

### 2. 重建venv
```bash
mv .venv .venv.broken
uv venv
uv pip install -r requirements.txt
```

### 3. CUDA版PyTorch
```bash
uv pip install "torch>=2.5" "torchvision>=0.20" "torchaudio" --index-url https://download.pytorch.org/whl/cu130
```

### 4. 验证CUDA + 补缺包

```bash
./.venv/Scripts/python.exe -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

常见缺包一次性补齐（重建venv后必装）：
```bash
uv pip install psutil sageattention sqlalchemy alembic pyyaml tqdm blake3
```

## WhatDreamsCost-ComfyUI（LTX Director 导演台）更新

GitHub：https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI

这是 LTX 视频剪辑/合成/多段编排的核心自定义节点包。凡哥用它做音频驱动视频（对口型）。

```bash
cd /d/SDkecheng/ComfyUI/custom_nodes/WhatDreamsCost-ComfyUI
git pull
```

**依赖同步**：更新此节点时，必须同时更新：
- `ComfyUI-LTXVideo`（git pull）
- `ComfyUI-KJNodes`（git pull）

**版本变化**：
- v2.0起 LTX Director 节点支持 IC-LoRA（需手动在Director界面加IC-LoRA轨道+加载IC-LoRA模型）
- ⚠️ **四个示例工作流全都不含IC-LoRA**：V3/2-Stage/3-Stage用 `MultiImageLoader+LTXSequencer`（首尾帧插值），Director 2 Hotfix 用 `LTXDirector` 但也没配 IC-LoRA。已验证JSON确认。
- **需要多参考图+音频驱动**→不要用WhatDreamsCost工作流，改用 `LiconStudio/LTX-2.3-Multiple-Subject-Reference` 仓库的工作流（见下方Licon MSR V2章节）

**Licon MSR V2（多参考图+音频驱动·2026-07-24新增）**：
- 仓库：https://huggingface.co/LiconStudio/LTX-2.3-Multiple-Subject-Reference
- 工作流：`LTX-2.3_MSR_sample_workflow_V2.json`（仓库自带，38节点，9个音频节点）
- LoRA：`LTX-2.3-Licon-MSR-V2.safetensors`（654MB）
- 需安装插件：`ComfyUI-Licon-MSR`
- 特点：`LiconMSR`节点处理多参考图融合，`LTXVSetAudioRefTokens` x2 处理音频驱动，`LowVRAMCheckpointLoader`加载基础模型
- 下载：
```bash
python -c "
import urllib.request
url='https://huggingface.co/LiconStudio/LTX-2.3-Multiple-Subject-Reference/resolve/main/LTX-2.3_MSR_sample_workflow_V2.json'
r=urllib.request.urlopen(url)
open('/d/SDkecheng/ComfyUI/user/default/workflows/Licon_MSR_V2_workflow.json','wb').write(r.read())
print('OK')
"
```
工作流默认加载 `ltx-2.3-22b-dev-fp8.safetensors`（来自 `szwagros/ltx-2.3-22b-dev-bf16-fp8`，约29.5GB含transformer_fp8=21.4GB+audio_vae+vocoder等组件）。凡哥本地有的是 `ltx-2.3-22b-distilled-1.1.safetensors`（46GB单文件）。RTX 5080 16GB通过ComfyUI-LTXVideo的CPU卸载机制均可运行。两者的真实差异见HuggingFace仓库文件列表——不要凭印象脑补。

**MSR V2 工作流关键节点ID（已验证·2026-07-24）**：
- `#21` `LTXVAudioVAELoader` — 加载 Audio VAE
- `#22` `LTXVEmptyLatentAudio` — 生成空白音频latent
- `#23` `LTXVConcatAVLatent` — 合并视频+音频latent

**MSR V2 加自定义音频步骤**（必须先在JSON中验证，再给ID，禁止脑补节点名）：
1. 右键空白→Add Node→搜 `VHS_LoadAudioUpload`（加载MP3/WAV）
2. 右键空白→Add Node→搜 `LTXVAudioVAEEncode`（编码音频为latent）
3. 选音频：点`VHS_LoadAudioUpload`→audio选文件
4. 连线：`VHS_LoadAudioUpload` audio → `LTXVAudioVAEEncode` audio
5. 连线：`#21` Audio VAE → `LTXVAudioVAEEncode` audio_vae
6. 连线：`LTXVAudioVAEEncode` Audio Latent → `#23` audio_latent
7. 断开：`#22` → `#23` 旧线

**VideoHelperSuite（VHS节点红叉）**：
```bash
cd custom_nodes/comfyui-videohelpersuite
rm -rf .git && git init
git remote add origin https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
git fetch --depth 1 origin main && git reset --hard FETCH_HEAD
```

## 恢复优先的故障处理节奏

凡哥反馈“修复任务太久”后，ComfyUI故障必须采用恢复优先，而不是把修复、全量体检、日志审计和归档绑在一起：

1. 先定位阻断启动的第一条真实异常，只修阻断项。
2. 修复后立即做最小验收：目标包可导入、ComfyUI进程存活、端口监听、主页或 `/system_stats` 返回 HTTP 200。
3. **HTTP 200后立即告诉凡哥“已经修好，可以使用”**，不要等待 ComfyUI-Manager 的 Registry/167项缓存拉取全部结束。
4. Triton、flash-attn、SoX、单个自定义节点缺包等非阻断警告，单独列为后续候选；未经确认不顺手修。
5. 不为验证核心启动去搜索全盘启动脚本；已知项目路径和端口时，直接用 `.venv/Scripts/python.exe main.py --port 18188` 验证即可。
6. 完整日志在本地筛选关键词，只把根因、修复动作和关键验收结果带回聊天；禁止把数百行日志原样灌入会话。
7. 技能、总控台和Git记录可以随后完成，但不得阻塞“可用了”的即时通知。

**凡哥的修复偏好（2026-08-07 明确表态）**：
- 🚫 **不接受 bypass/跳过节点作为最终方案**。凡哥说“我不跳过，必须修好”——节点报错要找到根因真修（升级依赖/换兼容版本），不能靠 Bypass 糊弄过去
- 但修复期间可以用 bypass 做**临时隔离**（区分是哪个节点/依赖在报错），修好后必须恢复
- 判断“修好”的标准：报错节点能真实执行，工作流跑通产出视频/音频，不是“不再报错但节点被禁用”

## 常见坑
| 故障 | 解决 |
|------|------|
| **端口18188被占用 / 数据库锁** | **上次ComfyUI没关！** 旧进程还在后台。`netstat -ano \| grep 18188`查PID→`taskkill //F //PID <PID>`杀进程→重启ComfyUI。不要改端口／改数据库路径——先查是不是旧进程没死。**git-bash里用`//F`双斜线（非`/F`）** |
| `ModuleNotFoundError` | `uv pip install xxx` |
| Torch CUDA disabled | 卸载CPU版→装cu130版 |
| git fetch失败 | 开v2rayN代理 |
| uv操作报权限 | 关掉ComfyUI所有python.exe |
| LTXVideo插件红叉 | kornia≥0.8不兼容→`uv pip install "kornia<0.8"` |
| uv sync清空旧包 | 不用uv sync！用`uv pip install -r requirements.txt` |
| 代码更新后ImportError | 必须同步更新venv——不能只换py文件不更新依赖 |
| `aiohttp` 报 `cannot import name '__version__'` | 先检查 `.venv/Lib/site-packages/aiohttp/__init__.py` 和 `aiohttp-*.dist-info/METADATA`；缺失/空目录即安装损坏。用 `env -u PYTHONPATH -u VIRTUAL_ENV uv pip install --reinstall "aiohttp>=3.11.8" --python .venv/Scripts/python.exe`，再验证 `from aiohttp import web` 和 `/system_stats`。只删除已确认0文件的旧 `dist-info` 残留；不用 `uv sync`。若旧 `inference-cli` 要求 `aiohttp<=3.10.11`，优先满足ComfyUI核心，不能把核心降回不兼容版本。 |
| Hermes终端串入错误venv | Hermes自身会设置 `PYTHONPATH`，直接调用ComfyUI Python可能误读 `D:/Hermes/hermes-agent/venv`。所有ComfyUI venv诊断/安装命令前加 `env -u PYTHONPATH -u VIRTUAL_ENV`。 |
| LiconMSR不加载 | 文件夹名不能带`-main`后缀→去掉 |
| **脑补节点名/ID给指令** | 🚫 **绝对禁止**。每次给ComfyUI操作指令前，必须`execute_code`跑Python读JSON验证节点类型+ID+连线。**多工作流对比时绝不能混淆节点ID**（本次就在四图音频工作流和MSR V2工作流间搞混了#1300和#21）。先验证再说话。 |
| **用户说\"工作流里没有X节点\"** | 先查 **ComfyUI UI 实际读的工作流目录** `user/default/workflows/*.json`，不是 `D:\下载\`！2026-08-07实测：改好的加速版在 `D:\下载\`，用户从UI打开的是 ComfyUI 自带目录里的旧版→当然没有LoRA。**改完的工作流必须复制到 `user/default/workflows/`**，让用户刷新后再打开。回话前先确认用户打开的是哪个文件——\"检查好了再说，别张嘴就来\"。 |
| 插件IMPORT FAILED | 关ComfyUI→`uv pip install -r 插件目录/requirements.txt`→重启 |
| LTXVideo加载失败 | kornia太新：`uv pip install "kornia<0.8"` 降级到0.7.4 |
| Windows不兼容插件 | dlib/fairseq/torchcrepe→无法修复，删掉插件；**triton 例外→装 `triton-windows` 社区版可修**（见下节） |

## 插件批量修复流程

```bash
# 关ComfyUI
taskkill /f /im python.exe

# 查所有失败插件的requirements
for dir in /d/SDkecheng/ComfyUI/custom_nodes/*/; do
    [ -f "$dir/requirements.txt" ] && cat "$dir/requirements.txt"
done

# 批量装（排除Windows不兼容的）
env -u PYTHONPATH -u VIRTUAL_ENV uv pip install [包列表]

# 重启ComfyUI，仍红X的删掉
rm -rf /d/SDkecheng/ComfyUI/custom_nodes/插件名
```

## 禁区
- 不用uv sync
- 不删custom_nodes/models/user
- 不全量替换代码不更新venv
- Windows不兼容插件清单见 `references/windows-incompatible-plugins.md`
- 不边修边试——先定方案再动手

## ComfyUI JSON 格式铁律（2026-08-06踩坑）

**API 格式 ≠ 工作流格式。修改前必须先确认格式类型。**

| 格式 | 识别特征 | 用途 | 支持分组/pos？ |
|------|---------|------|-------------|
| **API 格式** | `{"节点ID": {"inputs": {...}, "class_type": "..."}}` | 拖入画布加载、API调用 | ❌ 不支持 groups/pos |
| **工作流格式** | `{"nodes": [...], "links": [...], "groups": [...]}` | 完整画布布局 | ✅ 支持全部 |

**铁律**：
1. 凡哥给的 JSON → 先读第一个 key 判断格式。`"节点编号"` 在外层 → API 格式。
2. API 格式**禁止加 `groups`、`pos`** → 会导致节点全部消失。
3. 需要分组 → 让凡哥从 ComfyUI **菜单 Export→Workflow** 导出工作流格式 JSON。
4. 改参数（steps/sampler/LoRA）两种格式都能改，但**不要同时碰布局字段**。

## MiniMax H3 Turbo LoRA 加速

- LoRA 文件：`minimax_h3_turbo_4step.safetensors`（744MB）
- 来源：https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora（2026-08-05发布，early prototype）
- 放置：`ComfyUI/models/loras/`
- ⚠️ **节点类名不是 `LoadLora`（不存在）**：此 ComfyUI 版本正确类名是 `LoraLoaderBypassModelOnly`（界面显示"Load LoRA (Bypass, Model Only)"/"加载LoRA（旁路，仅模型）"）。用 `LoadLora` 会报"缺失节点包 LoadLora"。README 推荐的正是 Bypass Model Only 加载器
- 用法：`LoraLoaderBypassModelOnly` 接在 UNETLoader 之后 → 输出给 BasicGuider + BasicScheduler
- 参数调整：`steps: 25→4`，`sampler: res_multistep→euler`
- 预期加速：~5-6x
- ⚠️ 音频可能爆音（需要 DualClockSampler）

### ⚠️ 2026-08-07 实测三大坑（画质模糊/重影 + 无声音的根因）

**坑1：LoRA 键名必须转换，直接 LoadLora 无效**
- 作者原文件的键名**缺少 `diffusion_model.` 前缀**，普通 `LoadLora` 加载等于没加载 → 画质模糊/重影
- 必须用 `convert_h3_lora_for_comfyui.py`（DualClockSampler 仓库自带）转换键名前缀，输出 `minimax_h3_turbo_4step_comfyui.safetensors` 到 `models/loras/`
- 且必须用 **`Load LoRA (Bypass, Model Only)`**（加载LoRA（旁路，仅模型）），不能用普通合并式 LoadLora
- 转换只改键名前缀，不改数值/dtype/强度；转换后刷新模型列表
- 转换命令（2026-08-07 实测可用，**必须 unset PYTHONPATH**——否则会误读 Hermes venv 的 torch 报 WinError 126）：
```bash
cd /d/SDkecheng/ComfyUI/custom_nodes/ComfyUI-MiniMaxH3DualClockSampler
unset PYTHONPATH
/d/SDkecheng/ComfyUI/.venv/Scripts/python.exe convert_h3_lora_for_comfyui.py \
  "D:/SDkecheng/ComfyUI/models/loras/minimax_h3_turbo_4step.safetensors" \
  "D:/SDkecheng/ComfyUI/models/loras/minimax_h3_turbo_4step_comfyui.safetensors"
# 输出: "Converted: 518 tensor keys" + "Saved: ... 744MB" = 成功
```

**坑2（2026-08-07 实测修正）：pruned 主模型实测兼容——34GB 完整版不是必需的**
- 之前认为 `minimax_h3_ref2va_pruned_int8_convrot.safetensors` 缺 AdaLN 层——**实测错误**：pruned 模型含全部 40 个 `blocks.X.adaln_proj.linear.weight` 层
- ComfyUI 加载后自动给键加 `diffusion_model.` 前缀 → 与转换后 LoRA 键完全匹配
- 实测 `load_lora_for_models` 后 518 个 LoRA 键**全部匹配成功**（无 NOT LOADED 警告）
- 结论：**pruned + 转换后 LoRA 可用，无需下载 34GB 完整版**。完整版 `minimax_h3_ref2va_int8_convrot.safetensors`（34GB，`Comfy-Org/MiniMax-H3`）仅在 pruned 实测报错时才考虑
- 验证方法（加载 pruned + LoRA 看匹配数）：`load_diffusion_model_state_dict` → `load_lora_for_models(model, None, lora, 1.0, 0.0)`，无 `NOT LOADED` 警告即全匹配

**坑3：音频无声音/爆音 → ComfyUI 版本决定修法**
- 检查 `comfy.model_sampling.ModelSamplingAV` 是否存在：
  - 存在（ComfyUI ≥ commit bdcb886，2026-08-06 nightly）→ 官方已原生修复，直接用官方 `euler` 即可
  - 不存在（旧版）→ 必须装 `shuaixn/ComfyUI-MiniMaxH3DualClockSampler` 插件，把 `MiniMax H3 Dual-Clock Euler` 接到 `SamplerCustomAdvanced.sampler`

**症状诊断表**：
| 症状 | 根因 |
|------|------|
| 画面模糊+重影变形 | 坑1（LoRA键名没转，LoadLora静默无效）——pruned 主模型不是原因 |
| 完全没声音/爆音 | 坑3（ComfyUI旧版无 ModelSamplingAV） |
| 主体出不来/混沌一片 | 用了4步但没有Turbo LoRA生效（如架构不兼容时）——4步参数专为Turbo LoRA设计，普通25步模型不能用4步 |

### 🚫 坑4（2026-08-07 实测·致命）：Turbo LoRA 只兼容 FL2VA，不兼容 Ref2VA（全能参考）

**症状**：SamplerCustomAdvanced 执行时报 `RuntimeError: mat1 and mat2 shapes cannot be multiplied (3x8 and 2688x16)`，发生在 `adaln_proj.linear` 层。

**根因**：Turbo LoRA 是为 **FL2VA**（文生视频/图生视频）模型训练的，AdaLN 层维度 2688；用户全能参考工作流用的是 **Ref2VA**（多图+音频参考）模型，该层维度不同 → **架构级不兼容，不是配置问题，怎么调都跑不了**。README 原文明确只提 FL2VA 主模型。

**结论**：
- 全能参考（Ref2VA）工作流 **无法使用 Turbo LoRA 加速**——不要在这上面浪费时间
- 想加速全能参考 → 用 **TE-Speed**（见下节）
- Turbo LoRA 只留给纯 FL2VA 文生/图生视频场景

### ✅ TE-Speed-MiniMaxH3-OSS（2026-08-07 安装·全能参考的加速正解）

**为什么是它**：块缓存加速，不改模型架构 → **Ref2VA 全能参考完全兼容**（保留多图+音频+音色绑定），默认约提速 45%（抖音/B站流传的"H3加速30%"就是它）。对比：Turbo LoRA 只支持 FL2VA；Spectrum 是近似加速（轨迹会偏离，快速动作细节可能畸形）。

- 仓库：https://github.com/HELPMEEADICE/TE-Speed-MiniMaxH3-OSS （162⭐）
- 原理：50层DiT块循环，相邻步 sigma 差小时跳过尾部块重算，用缓存残差校正；三步条件（调度窗口内+sigma差<threshold+未超连续缓存上限）才走缓存步
- 安装：
```bash
cd /d/SDkecheng/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/HELPMEEADICE/TE-Speed-MiniMaxH3-OSS.git
cd TE-Speed-MiniMaxH3-OSS
python patch_model.py --comfy-ui "D:/SDkecheng/ComfyUI"   # 打钩子补丁，自动备份 model.py.te_speed.bak
# 验证：python patch_model.py --check --comfy-ui "D:/SDkecheng/ComfyUI" → "hooks already present"
# 回退：python patch_model.py --revert
```
- 节点注册名：`TESpeedMiniMaxH3`（验证：`curl http://127.0.0.1:18188/object_info` 搜 tespeed）
- 接线（在**原版25步**全能参考工作流上）：`UNETLoader → TESpeedMiniMaxH3 → BasicGuider/BasicScheduler`（删掉/禁用 Turbo LoRA 节点）
- 🚫 **TE-Speed 只有一个 MODEL 输出，没有 conditioning 输出**（`RETURN_TYPES = ("MODEL",)`）。BasicGuider（126）有两个输入：model ← TE-Speed ✅；**conditioning ← 136 MiniMaxH3ReferenceToVideo 的 conditioning 输出** ❌ 不能接 TE-Speed！接错 = 模型没有提示词和参考图 → 生成混沌没声音
- ✅ **验证接线只信 API 格式导出 JSON，不信截图**（2026-08-07 教训）：曾从截图误判用户把 conditioning 接到 TE-Speed（实际上用户导出 JSON 证明 126.conditioning ← 136.0 是正确的）——**看图判断接线不可靠，会冤枉用户**。正确流程：让用户从 ComfyUI 菜单导出 API 格式 JSON → 读 `inputs` 里的引用关系（如 `126.inputs.conditioning == ["136", 0]`）→ 用数据说话
- 参数默认即可：`processing_control_value=0.12`、`cache_depth=0.75`、`mcs=2`；`cache_depth=0` 关闭缓存（与官方流一致）
- ⚠️ **必须用原版步数（25）**，不能配4步——4步是Turbo LoRA专用参数，普通模型4步会主体都出不来
- 运行后控制台打印 `TE-Speed-MiniMaxH3(OSS): acceleration xx.x%` 实际加速比
- ✅ **验证是否真的生效**：`grep -i "TE-Speed\|acceleration" D:/SDkecheng/ComfyUI/user/comfyui_18188.log`——如果跑完 40 分钟但日志里**没有 acceleration 行**，说明 TE-Speed 节点根本没接上（工作流文件里也没有该节点），跑的是纯 25 步。检查工作流文件：`python -c "import json; wf=json.load(open('工作流.json')); print([k for k,v in wf.items() if 'TE' in str(v.get('class_type',''))])"`

### 🔍 TE-Speed 版本识别：OSS 版 vs 原始编译版（2026-08-07 实测）

**两个插件都注册节点类名 `TESpeedMiniMaxH3`，光看类名分不清版本。看日志文本和参数名**：

| 特征 | OSS 版（TE-Speed-MiniMaxH3-OSS） | 原始编译版（教程里那个） |
|------|--------------------------------|------------------------|
| 参数名 | `processing_control_value` / `processing_percent_1` / `processing_percent_2` | `threshold` / `start_percent` / `end_percent` |
| 启动日志 | （无） | `EasyCache enabled - threshold: 0.3, start_percent: 0.2, end_percent: 0.9` |
| 完成日志 | `TE-Speed-MiniMaxH3(OSS): acceleration xx.x%` | （未知格式） |
| 显示名 | "TE-Speed-MiniMaxH3 (OSS)" | "TE-Speed-MiniMaxH3" |

- 判断方法：`grep "EasyCache\|TE-Speed" user/comfyui_18188.log`——出现 `EasyCache enabled` 说明工作流里是**原始编译版**，不是 OSS 版
- 用户工作流 JSON 里的节点 `class_type: TESpeedMiniMaxH3` + 日志出现 `EasyCache enabled` → 加载的是原始编译版（可能装过但目录已删/被 OSS 顶掉，或用户从教程工作流导入的节点参数仍指原始版）
- 🚫 **不要假设工作流里那个 TE-Speed 节点就是 OSS 版**——参数对不上就先按日志文本核对版本，再决定改参数还是换节点

### ⚠️ 卡在 "Model Initializing ... 0/20" 且 GPU 100% 的排查（2026-08-07 实测）

**症状**：SageAttention 改 disabled 后能跑，但采样进度条卡 `0%| 0/20 [00:00<?, ?it/s, Model Initializing ...]`，GPU 100%、CPU 持续烧、output/ 无新文件、10+ 分钟一步不出。

**排查顺序（每步都是事实，不许猜）**：
1. `nvidia-smi` 看 GPU/显存；`curl http://127.0.0.1:18188/queue` 看任务是否真在跑（`queue_running` 有 1 个 = 活着）
2. `find ~/.triton/cache -newermt "启动时间" -type f` —— 有 Triton 新编译产物 = 在编内核（首次 SolAttn 要几分钟）；**无新文件 = 不是内核编译**
3. 日志最后一条时间 vs 当前时间——超过 10 分钟无新日志 = 卡在初始化阶段
4. 日志里 `EasyCache enabled - threshold: 0.3, start_percent: 0.2, end_percent: 0.9`（原始编译版 TE-Speed 的预计算）→ 嫌疑最大：EasyCache 初始化时在 GPU 上预计算，占满显存/算力但采样没开始
5. 有 `EasyCache enabled` 行 → 工作流里是原始编译版 TE-Speed，与 OSS 版参数名对不上（见上表）

**处理方向**：确认节点版本 → 若想用 OSS 版，把工作流里的节点换成 OSS 的 `TESpeedMiniMaxH3`（参数用 processing_control_value 系列）→ 或调原始版 EasyCache 参数。**先识别版本再动手，不猜**。

### 🎵 H3 音频接线是正确的不许乱改（2026-08-07 验证）

用户怀疑"自定义采样器没有音频信息，工作流没音频产出节点"——**官方模板确认接线正确**：
- H3 采样输出是 **NestedTensor**（一个张量打包视频latent + 音频latent）
- `VAEDecodeAudio` 内部检查 `latent.is_nested` 自动拆音频；`VAEDecode` 自动拆视频
- 官方模板 `video_minimax_h3_r2v.json`：`SamplerCustomAdvanced 输出0 → VAEDecodeAudio.samples` 和 `→ VAEDecode.samples` 同源
- 无声音的根因是步数不足（4步），不是接线

### 📏 H3 分辨率：宽高必须 32 的倍数

- 1280×720 **无效**（720÷32=22.5 有余数）→ 用 **1280×704**（704÷32=22）或 **1280×736**（736÷32=23）
- ResolutionSelector 节点（multiple=32）自动对齐：设 0.92MP → 输出 1312×736
- 帧数对齐 17：`max(5, round(a*24)) + (5 - (max(5, round(a*24)) % 17)) % 17`（时长→帧数）
- 官方 `align_frame_count`: 帧数 % 17 == 5

**⚠️ 大模型下载前必须查磁盘**（2026-08-07 教训）：
- 34GB 模型下到一半才发现 D 盘只剩 25G → 半成品文件占用 + 下载进程难杀（文件句柄 busy，`rm` 失败）
- **下载 >10GB 文件前先 `df -h /d` 检查剩余空间**；空间不足先删半成品再决定
- 杀下载进程后文件句柄可能延迟释放——`sleep 5` 后再删；`Device or resource busy` 时多等一轮
- 下载中断的半成品文件（5-20GB）必须删干净，否则磁盘雪上加霜

### 加速版工作流文件（2026-08-06 已生成）

- 加速版：`D:\下载\minimax_h3_turbo_加速版.json`（33节点，基于凡哥原文件改，不是重新生成）
- 改动点：node168 新增 `LoadLora`（minimax_h3_turbo_4step.safetensors）；node124 steps 25→4 且 model 指向 168；node123 sampler→euler；node126 guider model 指向 168
- 原文件：`D:\下载\minimax_h3_全能参考生视频.json`（凡哥发的工作流）
- ⚠️ 原文件的 138 节点 prompt 是完整版；若重新生成 JSON 会丢失 prompt，必须基于原文件改
- 下载 LoRA 用 Python urllib + 代理：`https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora/resolve/main/minimax_h3_turbo_4step.safetensors`（744MB，约1分钟）

## 🪟 Windows Triton 修复（triton-windows 社区版）— 2026-08-07 实测

**背景**：官方 triton 只有 Linux wheel（`triton>=2.2.0` 无 win_amd64），任何依赖 triton 的插件在 Windows 上 `IMPORT FAILED`（如 ComfyUI-SolAttn_triton、sageattention）。**但这是可修复的**——PyPI 有社区编译版 `triton-windows`（模块名仍是 `triton`，API 兼容）。

**安装（RTX 5080 / CUDA 13.0 / Python 3.12 实测）**：
```bash
cd /d/SDkecheng/ComfyUI
unset PYTHONPATH
uv pip install "triton-windows==3.7.1.post27" --python .venv/Scripts/python.exe
# 最新版本查：curl https://pypi.org/pypi/triton-windows/json 看 cp312+win_amd64 wheel
```
- 版本选择：**必须 cp312 + win_amd64 的 wheel**；RTX 5080（sm_120 Blackwell）需 triton ≥3.7（3.5/3.6 不支持 sm_120 内核，报 "cannot be used for the target device"）
- 验证：`.venv/Scripts/python.exe -c "import triton; print(triton.__version__)"` → 3.7.1
- 注意：venv 没有 pip 时用 uv（`python -m pip` 会报 No module named pip）

**⚠️ 插件 IMPORT FAILED 但日志里没有 traceback 时**：从 `user/comfyui_18188.log` 里 grep 插件名往前翻（`grep -B 5 -A 20 "插件目录名" user/comfyui_18188.log`），会看到真正的 `ModuleNotFoundError: No module named 'triton'` 及具体行号（如 `__init__.py line 23 → from ._autotune_log import` → `_autotune_log.py line 12 import triton`）。**先看日志找根因，别猜**。

## 🪟 SageAttention Windows 修复（sageattention 2.2.0 预编译 wheel）— 2026-08-07 实测

**背景**：PyPI 上 sageattention 最新只有 1.0.6（旧 API，只有 `sageattn` 函数），而 kjnodes 的 `PathchSageAttentionKJ` 节点需要 `sageattn_qk_int8_pv_fp8_cuda` 等新函数（2.x API）。症状：工作流执行时 `ImportError: cannot import name 'sageattn_qk_int8_pv_fp8_cuda' from 'sageattention'`。**更新 kjnodes 节点没用——问题在 sageattention 包版本，不在节点**。旧版 1.0.6 的函数是模块不是 callable（`attn_qk_int8_per_block` 是模块），差一代 API。

**Windows 预编译 wheel 来源（官方源码无 Windows 编译支持）**：
- `woct0rdho/SageAttention` releases —— **abi3 wheel**（`cp310-abi3` 兼容 Python 3.10+ 含 3.12）；有 `cu130torch2.10.0andhigher` 变体匹配 CUDA 13.0 + torch 2.13
- `sdbds/SageAttention-for-windows` releases —— cp311 具体版本（torch2.13.0+cu130 有匹配）
- 聚合索引：`BradPita/Win-AI-Wheelhouse` README（收录两个源的 wheel 表格）

**安装命令（RTX 5080 / CUDA 13.0 / Python 3.12 实测可用）**：
```bash
cd /d/下载
export HTTP_PROXY=http://127.0.0.1:10808 HTTPS_PROXY=http://127.0.0.1:10808
curl -sL --max-time 120 -o "sageattention-2.2.0+cu130torch2.10.0andhigher.post6-cp310-abi3-win_amd64.whl" \
  "https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post6/sageattention-2.2.0%2Bcu130torch2.10.0andhigher.post6-cp310-abi3-win_amd64.whl"
cd /d/SDkecheng/ComfyUI && unset PYTHONPATH
uv pip install --python .venv/Scripts/python.exe --force-reinstall "D:/下载/sageattention-2.2.0+cu130torch2.10.0andhigher.post6-cp310-abi3-win_amd64.whl"
```

⚠️ **uv 安装 wheel 必须保留原始文件名**（含版本/Python/CUDA 标签）——改名（如 `sageattention-2.2.0.whl`）会报 `error: The wheel filename is invalid: Must have a Python tag`。curl `-o` 指定完整原名。

**验证**：
```bash
.venv/Scripts/python.exe -c "import sageattention, importlib.metadata; print(importlib.metadata.version('sageattention')); print([n for n in ['sageattn_qk_int8_pv_fp8_cuda','sageattn_qk_int8_pv_fp16_cuda','sageattn_qk_int8_pv_fp16_triton','sageattn'] if hasattr(sageattention,n)])"
```

**模式选择**（kjnodes 节点 `sage_attention` 参数）：
- `sageattn_qk_int8_pv_fp8_cuda++`：int8 QK + fp8 PV，快但有轻微精度损失
- `auto`：纯 fp16（`sageattn`），画质最好
- `sageattn3` / `sageattn3_per_block_mean`：需要独立包 `sageattn3`（Blackwell 专用，不是 sageattention 包内函数）——RTX 50 系可另行安装

**⚠️ 坑5（2026-08-07 实测·致命）：fp8 模式在 H3 上直接 OOM（16GB 卡）**
- 症状：模型加载完成（显存 15.3/16GB 已用）→ GPU 0% → 执行时报 `torch.OutOfMemoryError: Allocation on device 0 would exceed allowed memory`，日志内存摘要 `Allocated 18519 MiB`（超卡 2GB+）
- 时间线证据（日志原文）：`22:42:14 Using sage attention mode: sageattn_qk_int8_pv_fp8_cuda++` → `22:42:15 Requested to load MiniMaxH3` → `22:42:20 OOM` —— **SageAttention 补丁挂上→主模型加载→5 秒后爆显存**
- **为什么之前能跑**：之前 sageattention 是 1.0.6，`PathchSageAttentionKJ` 节点 ImportError **从未生效**（模型走默认 attention）。升级 2.2.0 后节点真的挂上了 → fp8 内核在 H3 上分配 ~18.5GB → OOM。**"修好"一个静默失败的依赖 = 让之前被跳过的代码路径真正执行，可能暴露新问题**
- 🚫 **禁止脑补归因**：不要一上来怪"模型太大/VAE 加载 5 次/分辨率太高"——凡哥直接点破："没加速之前工作流是可以跑的，加速了跑不了了？"。**变更前能跑→变更后不能跑→根因在变更本身**（本次=SageAttention 升级），先查日志时间线锁定是谁在什么时刻分配的显存
- **排查顺序（逐步验证，不猜）**：① 把节点模式改 `disabled` → 跑（能跑=实锤 fp8 模式爆显存）② 再改 `auto`（fp16，显存小很多）→ 跑（能跑=H3 可用 auto 加速，只是不能上 fp8）③ 若 auto 也 OOM → H3 与 sageattn 不兼容，放弃 SageAttention 走 SolAttn/TE-Speed
- 显存排查命令：`nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv`；日志内存摘要：`grep -A 15 "PyTorch CUDA memory summary" user/comfyui_18188.log`

## SolAttn_triton（H3 稀疏注意力加速，与 TE-Speed 可叠加）

- 仓库：https://github.com/kijai/ComfyUI-SolAttn_triton （⭐180，2026-08-03 发布，活跃）
- 技术：NVIDIA Sol-Attn（免训练稀疏注意力，arXiv 2607.24027），Triton 内核
- 用途：加速 MiniMax H3 图像/视频生成；**与 TE-Speed 是两套独立机制**（块缓存 vs 稀疏注意力）→ 可串联叠加
- 安装：
```bash
cd /d/SDkecheng/ComfyUI/custom_nodes
git clone https://github.com/kijai/ComfyUI-SolAttn_triton.git
# 装完必须装 triton-windows（见上节），否则 IMPORT FAILED
```
- 节点：`SolAttnPatch`（显示名 "Patch Sol-Attn"）+ `SolAttnBlockProbe`（诊断）。走新版 `comfy_api.latest` 的 `comfy_entrypoint()` 注册，**没有 NODE_CLASS_MAPPINGS**——验证用 `curl http://127.0.0.1:18188/object_info | grep -i solattn`
- 参数（凡哥截图基准）：`tau=1.20, start_percent=0.20, end_percent=0.90, min_tokens=4096, morton=true, morton_curve=3d, int8_qk=false, sink_conditioning=exact_kv`
- ⚠️ 首次运行 Triton 内核要**编译**（几分钟），之后走缓存；属正常
- ⚠️ BETA 实验性：作者只测过 4090/5090，5080（sm_120）实测内核可加载但未完整跑通
- 内核模块验证（装完必测）：
```bash
unset PYTHONPATH && ./.venv/Scripts/python.exe -c "
import sys, types, importlib.util
pkg = types.ModuleType('sp'); pkg.__path__ = ['custom_nodes/ComfyUI-SolAttn_triton']; sys.modules['sp'] = pkg
for m in ['_tri_fwd', '_morton_h3', '_int8_fwd']:
    spec = importlib.util.spec_from_file_location(f'sp.{m}', f'custom_nodes/ComfyUI-SolAttn_triton/{m}.py')
    mod = importlib.util.module_from_spec(spec); sys.modules[f'sp.{m}'] = mod; spec.loader.exec_module(mod)
    print(f'OK {m}')"
```

### 启动 ComfyUI 验证

```bash
cd /d/SDkecheng/ComfyUI && ./.venv/Scripts/python.exe main.py --port 18188 --listen 127.0.0.1
# 验证：curl http://127.0.0.1:18188/system_stats → 200 + GPU 信息
```

## 重建venv后插件依赖恢复
重建venv会丢失所有插件依赖。修复流程：
1. 启动ComfyUI看启动日志，找 `IMPORT FAILED` 的插件
2. 逐个查 `custom_nodes/<插件名>/requirements.txt`
3. 批量 `uv pip install` 所有依赖
4. 注意：dlib/fairseq/torchcrepe在Windows上无法编译，对应的RVC/faceanalysis插件放弃；**triton可修复**（`triton-windows`社区版，见下节）
5. 重启验证——反复直到没有 `IMPORT FAILED`
