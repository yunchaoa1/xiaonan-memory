# Wan2.1 HuMo 多图参考+音频数字人 教程完整分析

> 视频路径: `/mnt/d/temp/humo_tutorial.mp4`
> 时长: 7分08秒 (427.85s)
> 分辨率: 2560×1600 (录屏)
> 教程标题: "22. Wan2.1 Humo多图参考+音频示例工作流"

---

## 一、工作流概述

这是一个基于 **Wan2.1 HuMo** 模型的 ComfyUI 工作流，核心功能：
1. **多张参考图**统一角色和产品外观
2. **音频驱动**口型同步（唇形同步）
3. 生成带音频的视频

演示了两组配置：
- **Run 1**: 女生 + 南瓜枕头 + "蔡徐坤.mp3"
- **Run 2**: 女生 + 白色头发毛绒玩具 + "蔡徐坤.mp3"

---

## 二、完整节点清单与连接关系

### 2.1 图像输入区（左侧）

| # | 节点名称 | 类型/插件 | 输入 | 输出 | 备注 |
|---|---------|----------|------|------|------|
| 1 | Load Image (上) | 内置 | — | IMAGE → Image Scale KJ v2 | 人物参考图: `image (22) (1).png` 或 `image (220).png` |
| 2 | Load Image (下) | 内置 | — | IMAGE → Image Scale KJ v2 | 产品参考图: `ComfyUI_00005_.png`(南瓜) / `ComfyUI_01102_png`(玩偶) |
| 3 | Image Scale KJ v2 ×2 | comfyui-kjnodes | IMAGE + width + height | IMAGE → Image Batch Combine | 两张图各连一个缩放节点 |
| 4 | Int (Width) ×2 | comfyui-kjnodes | — | → Image Scale KJ v2 | 值: **1280** |
| 5 | Int (Height) ×2 | comfyui-kjnodes | — | → Image Scale KJ v2 | 值: **720** |

### 2.2 模型加载区（顶部）

| # | 节点名称 | 插件 | 关键参数 | 输出 |
|---|---------|------|---------|------|
| 6 | **WanVideo 模型加载器** | kijai/WanVideoWrapper | 模型: `kijai-WAN2.1-HuMo-14B_fp16.safetensors`<br>精度: `fp16_fast`<br>量化: `disabled`<br>注意力: `sageattn`<br>rms_norm: `default` | MODEL → HuMo Embedding |
| 7 | **WanVideo Lora选择** | WanVideoWrapper | Lora: `wan_loral/Wan2_1_T2V_14B_light_2v_cdg_sdp_distill_lora_rank32.safetensors`<br>强度: **1.0000** | — |
| 8 | **WanVideo 设置块交换** | WanVideoWrapper | 交换层数: **30**<br>卸载文本嵌入: `false`<br>卸载图像嵌入: `false`<br>预取块: `1`<br>VAE交换块: `0`<br>非阻塞: `true` | — |
| 9 | **WanVideo 文本编码缓存** | WanVideoWrapper | 模型: `kijai-WAN\umt5-xxl-enc-fp8_e4m3fn.safetensors`<br>精度: `bf16`<br>量化: `disabled`<br>磁盘缓存: `true` | CLIP/CONDITIONING → HuMo Embedding |

### 2.3 提示词（Prompt）

| # | 节点 | 内容 |
|---|------|------|
| 10 | **CLIP Text Encode (Positive)** | Run 1: `一个女生拿着一个南瓜枕头在讲解功能。`<br>Run 2: `一个女生拿着一个白色头发的小型毛绒玩具在讲解功能` |
| 11 | **CLIP Text Encode (Negative)** | `色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景...` |

### 2.4 图像组合

| # | 节点 | 插件 | 参数 | 连接 |
|---|------|------|------|------|
| 12 | **图像组合批次 (多重)** | comfyui-kjnodes | 输入数量: **2** | 两张缩放后的图片 → Batch → HuMo Embedding |

### 2.5 HuMo 核心处理

| # | 节点 | 关键参数 |
|---|------|---------|
| 13 | **HuMo 嵌入** (WanVideoWrapper) | **帧数: 81**<br>宽度: 1280, 高度: 720<br>音频缩放: **1.00**<br>音频CFG缩放: **2.50**<br>音频起始: **0.00**<br>音频结束: **1.00**<br>分块VAE: **false** |

HuMo Embedding 是整个工作流的中枢，它接收：
- 图像 Batch（参考图）
- 音频特征（Whisper + MelBandRoFormer）
- 模型（VAE + 主模型）
- 文本编码（提示词）
- → 输出视频潜空间

### 2.6 采样

| # | 节点 | 参数 |
|---|------|------|
| 14 | **Float List (CFG调度)** | `[2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]` |
| 15 | **调度器** | `lcm` (配合Steps=8快速生成) |

### 2.7 音频处理区（紫色区域 "Audio input"）

| # | 节点名称 | 插件 | 模型/参数 | 连接 |
|---|---------|------|---------|------|
| 16 | **Load Audio** | 内置 | 文件: `蔡徐坤.mp3` (8秒) | → MelBandRoFormer 采样器 |
| 17 | **加载 Mel-Band RoFormer 模型** | MelBandRoFormer | 模型: `MelBandRoFormer_fp32.safetensors` | → MelBandRoFormer 采样器 |
| 18 | **Mel-Band RoFormer 采样器** | MelBandRoFormer | 分离人声/乐器 | 人声 → Normalize Audio Loudness<br>人声 → Whisper 编码器 |
| 19 | **规范化音频音量** | WanVideoWrapper | 模式: `lufs`<br>值: **-23.0** | → HuMo Embedding |
| 20 | **Whisper 模型加载器** | Whisper | 模型: `whisper_large_v3_encoder_fp16.safetensors`<br>精度: `fp16` | → Whisper 编码器 |
| 21 | **Whisper 编码器** | Whisper | — | → HuMo Embedding |
| 22 | **设置输入音频** | WanVideoWrapper | — | 连接音频到最终输出 |

### 2.8 输出

| # | 节点 | 说明 |
|---|------|------|
| 23 | **Preview Image** (右上) | 实时预览生成的视频 |
| 24 | VAE Decode (集成在 HuMo Embedding 中) | 分块VAE: false |

---

## 三、所有模型文件清单

| 用途 | 文件名 | 路径 |
|------|--------|------|
| 主模型 (14B) | `kijai-WAN2.1-HuMo-14B_fp16.safetensors` | ComfyUI/models/... |
| LoRA 蒸馏加速 | `Wan2_1_T2V_14B_light_2v_cdg_sdp_distill_lora_rank32.safetensors` | `wan_loral/` 子目录 |
| VAE | `kpz-WanVideo-1.1_VAE_bf16.safetensors` | ComfyUI/models/vae/ |
| 文本编码器 (T5 XXL) | `kijai-WAN\umt5-xxl-enc-fp8_e4m3fn.safetensors` | ComfyUI/models/... |
| Whisper 音频编码 | `whisper_large_v3_encoder_fp16.safetensors` | ComfyUI/models/... |
| 人声分离 | `MelBandRoFormer_fp32.safetensors` | ComfyUI/models/... |

另有备选模型名（截图中可见但不完全一致）:
- `kpz-WanNext-1.3B-Humo-FP16.safetensors`
- `kijai-WAN2_ViD_T2V_14B_light_2v_cdg_sdp_distill_lora_rank32.safetensors`

---

## 四、"多图参考"实现细节

### 4.1 节点链路

```
Load Image (人物) ──→ Image Scale KJ v2 ──┐
                                          ├──→ 图像组合批次（输入数=2）──→ HuMo Embedding
Load Image (产品) ──→ Image Scale KJ v2 ──┘
```

### 4.2 Image Scale KJ v2 参数（关键！）

| 参数 | 值 | 说明 |
|------|-----|------|
| 缩放方法 | `lanczos` | 高质量缩放 |
| 固定宽高比 | **`pad`** ← 老师强调！ | 填充而非裁剪 |
| 填充颜色 | `255, 255, 255` | 白色填充 |
| 裁剪位置 | `center` | 居中 |
| 缩放因子 | `16` | — |
| 设备 | `cpu` | — |
| 输出分辨率 | 1280×720 | — |

### 4.3 ⚠️ 老师特别强调的"对齐"技巧

> "对于产品和人物的一个对齐是非常重要的"

- **必须用 PAD 模式，不能用 Crop**：如果用 Crop 裁剪，可能会把人脸的上半部分切掉
- K.J. 作者本人回复：对齐（Alignment）是 HuMo 模型效果好不好的关键
- 两张参考图都要缩放到相同的 1280×720 分辨率，才能正确 Batch 到一起
- 建议最佳分辨率：**1280×720** 或 **832×480**（原始默认值效果最好）
- 添加更多参考图：修改"图像组合批次"节点的 `输入数量`

---

## 五、音频数字人完整链路

### 5.1 音频处理流程

```
蔡徐坤.mp3 (8秒)
    │
    ▼
Mel-Band RoFormer 采样器 ──── 分离出 ──┬── 人声 (干净语音)
    │                                   │
    │                                   ▼
    │                          规范化音频音量 (LUFS: -23.0)
    │                                   │
    │                                   ▼
    │                              HuMo Embedding
    │
    ├── Whisper Large V3 编码器 ──────────────► HuMo Embedding
    │   (whisper_large_v3_encoder_fp16)
    │
    └── 乐器音频 (丢弃)
```

### 5.2 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 音频文件 | `蔡徐坤.mp3` | 约8秒 ("全民制作人们大家好，我是练习时长两年半...") |
| 人声分离模型 | MelBandRoFormer_fp32 | 分离人声和背景音乐 |
| 响度归一化 | **-23.0 LUFS** | 防止音量波动影响口型精度 |
| Whisper 模型 | whisper_large_v3_encoder_fp16 | 音频特征编码 |
| 音频缩放 | 1.00 | HuMo Embedding 中 |
| 音频 CFG 缩放 | **2.50** | 高于普通 CFG(2.0)，强调音频驱动 |
| 音频起止百分比 | 0.00 / 1.00 | 全程跟随音频 |

### 5.3 音频与视频的关系

- 视频帧数 81 帧 @ 25fps = **约 3.24 秒**
- 音频时长 = **8 秒**
- **音频会被自动裁剪前 3 秒**，只保留视频时长的部分
- 最终视频带有音频（口型同步）

---

## 六、最终参数汇总

| 参数类别 | 参数 | 值 |
|---------|------|-----|
| **分辨率** | Width × Height | **1280 × 720** |
| **帧率** | FPS | **25** fps |
| **帧数** | Frames | **81** (≈3.24秒) |
| **采样步数** | Steps | **8** |
| **调度器** | Scheduler | **LCM** |
| **CFG Scale** | 基础 CFG | **[2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]** (动态) |
| **音频 CFG** | Audio CFG Scale | **2.50** |
| **Seed** | — | 未显示（默认随机） |
| **主模型** | Checkpoint | Wan2.1-HuMo-14B fp16_fast |
| **LoRA 强度** | Strength | **1.00** |
| **Block Swap** | 交换层数 | **30** (48GB 显存) |
| **分块 VAE** | Chunk VAE | **false** |
| **注意力机制** | Attention | **sageattn** (加速) |

---

## 七、老师口述操作步骤与技巧

### 7.1 完整操作步骤

1. **拖入工作流** → ComfyUI
2. **上传参考图** → 至少 2 张：人物 + 产品
3. **写提示词** → 尽量详细描述人物衣着、动作、产品外观
4. **上传音频** → 干净的人声（通过 MelBandRoFormer 分离）
5. **调整 Block Swap** → 根据显存设置（48GB 设 30）
6. **点击运行** → 等待生成

### 7.2 ⚠️ 注意事项和"坑"

| # | 老师提醒 | 详细说明 |
|---|---------|---------|
| 1 | **对齐是关键** | "对于产品和人物的一个对齐是非常重要的"——两张参考图分辨率必须一致且内容对齐 |
| 2 | **用 PAD 别用 Crop** | "如果是Crop的话，它会根据这个分辨率做一个裁剪，可能会把人的脸的上半部分给裁掉" |
| 3 | **提示词写详细** | "描述的也精准，它复现的效果可能会更好一点，一致性可能会更好"——衣服颜色、发型、动作都写进去 |
| 4 | **上传干净人声** | "上传干净的人声音频"——必须用 MelBandRoFormer 分离人声，去掉背景音乐 |
| 5 | **显存管理** | "根据显存去设置一下Block Swap"——14B 模型很大，48GB 给了 30 层交换 |
| 6 | **HuMo 有抖动** | "用 Humor 生成的视频，我们看出来他经常会有这种小动作，就是一直在抖动的情况"——这是模型已知局限 |
| 7 | **最佳分辨率** | "Seems to work best with original defaults of 1280x720 and 832x480"——K.J. 作者建议的默认分辨率 |
| 8 | **音量归一化** | "-23.0 LUFS"——防止音量过大过小导致口型不稳定 |

### 7.3 老师的口头总结

> "注意自己上传产品和人物的一个对齐方式，再注意提示的书写，尽可能的详细一点，其次设置合适的一个帧数，然后上传干净的人声音频，同时根据显存去设置一下Block Swap，然后点击运行去拿到最终的结果。"

---

## 八、提示词内容

### Run 1（南瓜）

- **正向**: `一个女生拿着一个南瓜枕头在讲解功能。`
- **负向**: `色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景...`

### Run 2（毛绒玩具）

- **正向**: `一个女生拿着一个白色头发的小型毛绒玩具在讲解功能`
- **负向**: 同上（未变）

### 老师建议的提示词写法

> "比如说他拿着一个什么样的毛绒玩具在讲解，或者说是怎样的一个女生，比如说这里他是穿着一个白色的内搭，加上一个黄色的外套，这样的一个形象，都可以把它写出来"

---

## 九、输出文件格式和保存路径

| 项目 | 说明 |
|------|------|
| 输出类型 | 视频（带音频） |
| 分辨率 | 1280×720 |
| 帧率 | 25fps |
| 帧数 | 81 帧（约 3.24 秒） |
| 视频编码 | MP4 (H.264) |
| 音频 | 嵌入音频（原音频裁剪前 3 秒） |
| 保存节点 | Preview Image / 可能的 VHS Video Combine |
| 输出路径 | ComfyUI 默认 output 目录（未显示自定义路径） |

---

## 十、工作流完整数据流图

```
                      ┌─────────────────────────────────┐
                      │     模型加载 (Top)               │
                      │  ┌───────────────────────────┐  │
                      │  │ Wan2.1-HuMo-14B fp16_fast │  │
                      │  │ + LoRA (rank32, str=1.0)  │  │
                      │  │ + Block Swap (30 layers)  │  │
                      │  │ + sageattn 加速           │  │
                      │  └───────────┬───────────────┘  │
                      │              │ MODEL             │
                      └──────────────┼──────────────────┘
                                     │
  ┌──────────────┐    ┌──────────────┼──────────────────┐
  │ 参考图1(人物) │    │              │                  │
  │ Image Scale  │    │   ┌──────────▼─────────────┐    │
  │  1280×720    ├────┼──►│                        │    │
  │  PAD模式     │    │   │    HuMo Embedding      │    │
  └──────────────┘    │   │                        │    │
                      │   │  Frames: 81            │    │
  ┌──────────────┐    │   │  Resolution: 1280×720  │    │
  │ 参考图2(产品) │    │   │  Audio Scale: 1.00     │    │
  │ Image Scale  │    │   │  Audio CFG: 2.50       │    │
  │  1280×720    ├────┼──►│  Chunk VAE: false      │    │
  │  PAD模式     │    │   └──────────┬─────────────┘    │
  └──────────────┘    │              │                  │
                      │   ┌──────────┼──────────┐       │
  ┌──────────────┐    │   │          │          │       │
  │ 提示词        │    │   │  ┌───────▼──────┐   │       │
  │ CLIP Encode  ├────┼──►│  │  采样器      │   │       │
  │ (正+负)      │    │   │  │ LCM Scheduler│   │       │
  └──────────────┘    │   │  │ Steps: 8     │   │       │
                      │   │  │ CFG: 2.0-1.0 │   │       │
  ┌──────────────────┐│   │  └───────┬──────┘   │       │
  │ Audio Input      ││   │          │          │       │
  │                  ││   │  ┌───────▼──────┐   │       │
  │ 蔡徐坤.mp3 (8s)  ││   │  │  VAE Decode  │   │       │
  │   ↓              ││   │  └───────┬──────┘   │       │
  │ MelBandRoFormer  ││   │          │          │       │
  │   ↓ (人声分离)   ││   │  ┌───────▼──────┐   │       │
  │ Normalize -23LUFS├┼──►│  │Preview/Save  │   │       │
  │   ↓              ││   │  │ 1280×720@25  │   │       │
  │ Whisper Large V3 ││   │  │ ≈3秒视频+音频│   │       │
  │   ↓ (音频特征)   ││   │  └──────────────┘   │       │
  └──────────────────┘│   └─────────────────────┘       │
                      └─────────────────────────────────┘
```

---

## 十一、已知局限

1. **HuMo 视频有抖动**: "用 Humor 生成的视频经常会有这种小动作，就是一直在抖动的情况"——这是模型固有特征
2. **14B 模型显存需求大**: 1280×720 + LoRA，48GB 显存需 30 层 Block Swap
3. **音频自动裁剪**: 视频时长(81帧≈3秒)比音频(8秒)短，音频只保留前段
4. **需要干净人声**: 背景音乐会影响口型精度，必须分离
