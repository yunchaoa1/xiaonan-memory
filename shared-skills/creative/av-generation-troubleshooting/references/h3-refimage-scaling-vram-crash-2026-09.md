# H3 二采（latent 放大）暴显存崩：根因＝参考图未缩放（2026-09-18 云端实测 + UP 官方教程实证）

环境：云电脑 智算云扉 RTX 5090 32GB / ComfyUI 0.35.0 / torch 2.14.0+cu130 / 122GB RAM
工作流：`4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json`
（= UP **Astral星芒**《MiniMax-H3 全能生视频V4 工作流 latent分块二采版 (可直出2K)》的本地提示词改造版）
触发：一采 960×544 → 二采 `MinimaxH3LatentUpscaler3D` scale **2.0** → 1920×1088

## 症状（日志实锤，可作错误串检索）

```
[MinimaxH3-3D] Latent 60x34 -> 120x68 | Pixels 1920x1088 | scale=2.000
[INFO] Requested to load MiniMaxH3
[INFO] 0 models unloaded.                       ← 一采模型未卸载（峰值主因之一）
[W... CUDAMallocAsyncAllocator.cpp:377] [cudaMallocAsync] recovered from an allocation failure by trimming the pool and retrying.
terminate called after throwing an instance of 'c10::AcceleratorError'
  what():  CUDA error: invalid argument
  Returning 1 (CUDA_ERROR_INVALID_VALUE) from cuMemFreeAsync
Exception raised from free_impl at c10/cuda/CUDAMallocAsyncAllocator.cpp:207
frame #5: c10::TensorImpl::~TensorImpl()
[INFO] Fatal Python error: Aborted
```

二采前显存：`VRAMdebug: free memory before: 5,179,044,536`（32GB 卡仅剩 5.18GB）、`freed memory: 0`。

## 根因（UP 官方教程 + 插件源码 双证据）

1. **UP 教程原话**（Astral星芒，《单采2K VS 双采分块2K 谁是MiniMaxH3王者？》，B站 `BV1VBY56JEH3`，17:05）：
   **「你传入的图片如果是 2K 的，那么它传进去之后参考的图片就是 2K 的，这个时候就很容易暴显存」**；
   解法：「把你的图片在传进去这个素材之前，自己先进行一个缩放，缩放到一定的边……按自己实际的显存情况微调」（他 16:05–18:15 演示了 `match` 模式 / `最大值` 模式两种选法）。
2. **插件源码**（`ComfyUI-MiniMax-ContextIR/h3_fant_nodes.py`）：`MiniMaxH3ReferenceSplitter` 的参数
   `short_edge_max`，tooltip 原文 **`Short edge max pixels; 0 = no scaling.`** —— **0 = 参考图完全不缩放**（只缩不放）。
   本工作流取值即 **0**；`align_to` = 16（缩放后的像素对齐）。
3. **实际喂进去的参考图 = 1440×2560（3.7MP）**（日志 `[comfyUI-llama-TE] Input image auto-compressed: 1440x2560 -> 576x1024` 反证原图尺寸；那是 llama-TE 内部压缩，不是 H3 参考图输入）。
4. 合成因果：一采只需 0.52MP、二采 2.0×→1920×1088，而参考图按 **3.7MP 原样参与** → 显存需求远超 32GB → 分配失败 → 分配器 trim 池 → 释放路径报 INVALID_VALUE → 进程 Aborted。
   （`cuMemFreeAsync` 的 INVALID_VALUE 在 NVIDIA 文档里的判据正是"释放时的 location/类型与 pool 不匹配"= 分配器已被压到状态不一致。）

## 正解（按 UP 官方）

1. **`MiniMaxH3ReferenceSplitter.short_edge_max` 从 `0` 改成合适值**（`align_to` 保持 16）：

| 值 | 效果 | 用法 |
|---|---|---|
| **544** | 缩到一采短边 | **先试这个**（最省显存） |
| 816 | 折中 | 显存有余量、画质要求高时 |
| 1088 | 接近二采短边 | 显存充裕时 |

2. 等价做法（UP 也这么讲）：**喂之前先把参考图文件缩放到合适边长**。
3. 继续压峰值（次选）：UP **原版**二采倍率是 **1.5**（960×544×1.5=1440×816），我们改成 2.0 才拿到 1088P；若画质/显存冲突，降回 1.5 是 UP 标定过的档。

## ⛔ 被凡哥否定的自创方案（别再走这条）

本节最初（同一次会话中）被写成「cudaMallocAsync 分配器在高压下崩 → 启动加 `--disable-cuda-malloc`」并把该结论写进了本 skill。
**凡哥当场纠正：「你去看这个 up 主的官方信息，从那里找方案修，不要自己瞎试」** —— 该结论已作废，原因：

- `cuMemFreeAsync CUDA_ERROR_INVALID_VALUE` 是**显存被压到极限的症状**，不是独立病根；加 `--disable-cuda-malloc` 只是把崩溃点挪走，**不解决"3.7MP 参考图硬喂二采"**。
- **纪律**：H3 / 工作流类故障的根因，必须来自 ① **UP 官方教程或网盘说明** ② **工作流 json 的 MarkdownNote / 作者主页** ③ **插件源码**；三方对齐后才给方案。自己的推断只能标"待验证"，不得当结论写进 skill 或交付凡哥。

## 归因纪律（同一次会话的第二个纠正）

凡哥纠正：「**不是小黄瓜的**，我们的这个工作流的特点是有提示词优化功能的，你忘记了？」——
**工作流身份不要凭印象/不要靠旧笔记**，直接从 **工作流 json 的 MarkdownNote 节点**读：

```python
import json
d = json.load(open(WORKFLOW, encoding="utf-8"))
for n in d["nodes"]:
    if n["type"] == "MarkdownNote":
        print(n.get("title"), "|", str(n.get("widgets_values"))[:800])
```

本例读出的原话：`【AI视频】MiniMax-H3 全能生视频V4 工作流 latent分块二采版 (可直出2K)`／`【特点】…官方skill自动提示词；音频锁定；低显存二次采样；远景不崩脸`／`【作者】Astral星芒`／`【工作流使用讲解】https://space.bilibili.com/176339505`。
**辨识特征 = 本地提示词优化（QwenTE / comfyUI-llama-TE 反推提示词）**；「啦啦啦的小黄瓜」是**另一套**（LTX2.5 放大方案）的作者，那套已被凡哥否掉。

## 取证命令（复用）

```bash
awk '/got prompt/{buf=""} {buf=buf"\n"$0} END{print buf}' comfyui.log | head -80   # 最后任务完整段（含栈顶）
grep -n -E "To see the GUI go to|got prompt|Requested to load|Prompt executed|Fatal Python error|CUDA error|Allocation on device|out of memory" comfyui.log | tail -50   # 时间线
sed -n 'X,Yp' comfyui.log                                                          # 崩溃前上下文
```
