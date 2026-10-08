# H3 × ComfyUI 0.37：sage patch 报 `Tensor input must be on CUDA` —— 根因已定位（2026-10-08 云端）

> **状态：根因已确认（硬证据）；修法一条都还没端到端验证。**
> 「根因」「已证伪」两段可照抄引用；「修法候选」段**别当「已修好」转述**。
> 本文件取代旧名 `h3-037-sage-tensor-cuda-open-issue.md`（那份标的是「未解决」，已过时）。

## 根因（硬证据，可照抄）

**sageattention 的预编译轮子与当前 PyTorch 大版本 ABI 不匹配** —— 与 ComfyUI、工作流、KJNodes 补丁**全无关系**。

判据 = **在 ComfyUI 之外做最小隔离复现**，一条命令锤死：

```bash
cd <ComfyUI> && <venv>/bin/python - <<'PY'
import torch, sageattention
print("torch:", torch.__version__, "| torch.cuda:", torch.version.cuda)
from sageattention.quant import per_warp_int8
q = torch.randn(1, 4096, 16, 64, device="cuda", dtype=torch.bfloat16)
k = torch.randn(1, 4096, 16, 64, device="cuda", dtype=torch.bfloat16)
try:
    o = per_warp_int8(q, k, km=k.mean(dim=1, keepdim=True), tensor_layout="NHD", BLKQ=128, WARPQ=32, BLKK=64)
    print(">>> SAGE OK", o[0].device, o[0].shape)
except Exception as e:
    print(">>> SAGE FAILED:", type(e).__name__, e)
PY
```

实测输出：`>>> FAILED: RuntimeError Tensor input must be on CUDA`
—— 纯净进程、纯 cuda 张量、零 ComfyUI 参与，照样炸 ⇒ **是这个包本身对不上**。

机理（🟡 推断，但自洽解释全部观测）：C++ 扩展须**与 PyTorch 精确 ABI 对齐**才认得出张量；跨大版本时 Python 层读到 `t.device.type == "cuda"`，C++ 层读同一张量却认不出设备 → 恰报这句话。报错点是 `sageattention/quant.py:172` 的 `_fused.quant_per_warp_int8_cuda(q, q_int8, q_scale, ...)`，而它前面 153/154/169/170 行**全部显式写了 `device=q.device`** ⇒ 「输出缓冲建在 CPU」这条路一并排除。

## 已证伪的假设（别再重跑）

| 曾经的假设 | 证伪方式（本轮实测） |
|---|---|
| 张量被 0.37 的 DynamicVRAM 留在 CPU | 在 `_sageattn_int8_fp8_nhd` 里插 `if not all(t.device.type=="cuda" ...): print(...)` + 搬移 —— **一行都没打印** ⇒ q/k/v 本来就是 cuda；搬移补丁照旧报同样错 |
| `--disable-comfy-compiler` 能救 | 本轮 `** Arguments:` 行**确证**该 flag 已带上（上一轮是没生效就重跑），**仍报同样错** |
| KJNodes 版本差异（8/28 vs 9/13） | `git diff 2bf3bd9 d3cfe21 -- nodes/ltxv_nodes.py` **完全为空**，一字未改 |
| 降 ComfyUI 回 v0.30.0 绕开 | 工作流按 ≥0.35 官方核心节点对齐保存，0.30 缺 `comfy_extras/nodes_sparse_attention.py` → widgets 错位、校验秒退；且老基线（v0.30.0 / cu128 / `/home/waas`）2026-10-08 已全部释放 |
| `per_warp_int8` 的缓冲默认建在 CPU | 源码 153/154/169/170 行全部 `device=q.device` |

**两个通用判据（本轮各用上一次，值得固化）**：
- **`print` 放进条件里** —— 条件不成立就不打印；「一个字都没打印」= 你的假设是错的。本次正是靠它把「张量在 CPU」整条否掉。
- **报错栈行号位移 = 补丁确实落地** —— 行号 1945→1947→1952 与插入行数精确对应，可区分「改了没生效」与「生效了但没用」。

## 轮子选型：预编译 CUDA 扩展的 ABI 标签纪律

**文件名里没有 torch 版本标签的轮子 = 红旗**，跨 torch 大版本必然对不上，别拿它顶「之前跑通的那版」。

| 源 | 有什么 | 备注 |
|---|---|---|
| `Kijai/PrecompiledWheels`（HF） | `sageattention-2.2.0-cp312-cp312-linux_x86_64.whl`（14.6MB，**2025-07-01**） | 「之前跑通」用的就是它 —— 那是 **torch 2.8 时代**；torch 2.13+ 会 `undefined symbol: c10::impl::cow::materialize_cow_storage` |
| `snw35/sageattention-wheel`（GH） | tag `cu12-2.2.0-cu13-2.2.0`（2026-01-30）的 `+cu12` / `+cu13` linux cp312；另有 **1.78GB** 的 `+cu13-cp312-manylinux_2_39` 自包含版 | **名字里无 torch 标签** ⇒ 本轮装的就是它，即故障轮子 |
| `vjump21848/sageattention-pre-compiled-wheel`（HF） | `sageattention-2.2.0+cu130.torch210.sm80.86.89.120-cp312-cp312-linux_x86_64.whl`（33.5MB） | **Linux 侧最接近的候选**：带 `torch210` + `sm120`；torch 2.10 编、跑在 2.12 上能否过**未实测** |
| `pixeloven/SageAttention-Wheels`（GH） | `...+cu130.torch2.13.0.sm120-cp312-cp312-linux_x86_64.whl` | 按 sm80/86/89/90/120 分文件 + `BUILD-INFO-<arch>.txt` 可查证 |
| `woct0rdho/SageAttention`（GH） | **只有 Windows wheel（无 Linux）** | 但其 `torch2.10.0andhigher` 的 ABI3 轮子被 ComfyUI 安装器标注为**已在 torch 2.12 + RTX 5090 上端到端验证** ⇒ Linux 要的是「同代 ABI3 构建」，不是这个文件本身 |

理想匹配五件套：`linux_x86_64` + `cp312` + CUDA 大版本对得上 + **torch 版本标签对得上** + `sm120`。

**新轮子装完第一件事**：验 KJNodes 的 6 符号探针（`per_thread_int8_triton` / `per_warp_int8_cuda` / `per_block_int8_triton` / `per_channel_fp8` / `get_cuda_arch_versions` / `attn_false`）。
另注意 **KJNodes issue #736**：新版轮子把算子挪到 `torch.ops.sageattention_qattn_sm89`，而 `_resolve_qattn()`（`ltxv_nodes.py:1715`）只探 `sageattention.core` 的模块属性、**不查 `torch.ops`** → 换新轮子后若转报 `not new enough`，按 #736 的修法加 `torch.ops` 候选。

## 修法候选（**均未端到端验证**，按代价排序）

1. **换一个带对 torch 标签的 Linux 轮子**（首选，代价最小）—— 候选见上表。
2. **用当前环境就地编译**（ABI 天生对齐，理论上最确定）—— 已知拦路虎：torch 的 `_check_cuda_version` 硬性要求 **nvcc 的 CUDA major == torch 的 CUDA major**（无环境变量可跳）；且 thu-ml main 在 torch 2.13/2.14 上曾被报 `'sizes' is not a member of 'at::symtab'` 编不过。真要走：先 `which nvcc` + `nvcc --version` 确认 major 对得上，再 `TORCH_CUDA_ARCH_LIST=12.0 MAX_JOBS=4 <venv>/bin/pip install . --no-build-isolation`（后台 nohup，15~40 分钟）。
3. **`Ctrl+B` 旁路 `MiniMaxH3MemoryEfficientSageAttentionPatch`**（保底，能立刻出片）—— 该节点自标 `EXPERIMENTAL`、作用只是降峰值显存；旁路后走 ComfyUI 原生 attention，`Ctrl+B` **自动直通输入→输出、无需改线**。代价：失去显存优化（长视频有爆显存风险）+ 偏离 UP 标准版 ⇒ **属凡哥决策事项，摆事实给选项、别自己替他绕**。

## 症状与签名（复现用）

```
RuntimeError: Tensor input must be on CUDA
  ComfyUI-KJNodes/nodes/ltxv_nodes.py:2106/2113  minimax_sageattn_forward
  ComfyUI-KJNodes/nodes/ltxv_nodes.py:1945/1952  _sageattn_int8_fp8_nhd → per_warp_int8_cuda(q, k, ...)
  sageattention/quant.py:172                     _fused.quant_per_warp_int8_cuda(q, ...)
```

触发时机固定：模型加载完 → `0/6 it, Model Initializing ...` → 立刻炸；`Prompt executed in ~50 seconds`。
环境：ComfyUI 0.37.0（`73c9bad4`）、torch **2.12.1+cu130**、RTX 5090 32G、`--disable-cuda-malloc`；日志另见 `DynamicVRAM support detected and enabled` + `Using async weight offloading with 2 streams`（**均与本病无关，别再当变量去动**）。

## 环境侧前置坑（本次已全部修好，属「下一层」）

`llama_cpp` 缺失 → JamePeng `+cu130` wheel；sage 6 符号探针 → `snw35 +cu13`；`CXXABI_1.3.15` → 软链系统 libstdc++；`llama.cpp GPU offload: no` → `ggml_backend_load_all_from_path(<lib目录>)`（细节见 `035-node-migration.md` §四/§五/§六）。

0.37 相关启动开关（`main.py --help` 实测）：`--disable-comfy-compiler` · `--disable-cuda-graphs` · `--disable-async-offload` · `--enable/--disable-dynamic-vram` · `--use-sage-attention` · `--disable-cuda-malloc` · `--async-offload [N]`。「Comfy model compiler」真身在 `comfy/model_prefetch.py`。

## 操作纪律（本轮真金白银浪费掉的两轮，务必遵守）

1. **命令块里只能有命令。** 把 `--help` 的参数说明行紧挨命令块放 → 凡哥当场问「**这个是给我去云电脑上跑的命令吗？**」，然后跑了上一条 → 白跑一轮。规矩：一个代码块 = **一条**完整命令；解释放块外；**新增参数时明确写「和上一条的区别就是多了 `XXX` 这个词」**。
2. **带新参数重启后先自证生效，再让他跑。** 自证：`ps -ef | grep -v grep | grep "[m]ain.py"` 看见该 flag，或看报错报告的 `** Arguments:` 行 —— **ComfyUI Error Report 自带这个字段，是最省事的判据**。
3. `** Arguments:` 行还会暴露凡哥长期带着的 flag（云端 H3 的 `--disable-cuda-malloc` 就是），别当可疑变量去动。
