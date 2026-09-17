# 0.35 官方核心节点 vs 社区节点：参数表迁移 & 依赖库（2026-09-10 实测）

## 一、BlockSparseAttention：widget 值整体错位

**症状**（跑 UP 标准版工作流时，云端 0.35）：

```
Failed to validate prompt for output 227:
* BlockSparseAttention 1297:1369:
  - Value not in list: sink_conditioning: 256 not in ['exact_kv', 'exact_kv_and_rows', 'off']
  - Value 1.3 bigger than max of 1.0: start_percent
  - Value 12288 bigger than max of 256: extra_tokens
  - Failed to convert an input value to a INT value: min_tokens, , invalid literal for int() with base 10: ''
Output will be ignored
```

整条 prompt 秒退（`Prompt executed in 0.34 seconds`），看起来像节点坏了。

**根因**：工作流是用**社区版节点**保存的（参数表不同），而云端 0.35 注册的是**官方核心节点**——`comfy_extras/nodes_sparse_attention.py`，PR #16072（2026-09-06 并入，官方 wiki 有专文）。官方 `selection` 的 options 是短名 `["sol-attn", "sla", "vsa"]`，工作流里存的是社区版**显示名** `"Sol-Attn (adaptive tau)"` → 值不在 options → DynamicCombo 解析失败 → **后续 widget 值整体按错误位置解读（错位一格）** → 报出一串"参数名↔值"对不上的错误。

**官方定义**（云端源码实证：`sed -n '/class BlockSparseAttention/,/^class /p' comfy_extras/nodes_sparse_attention.py | head -95`）：

| input | 合法值 | 默认 |
|---|---|---|
| selection | `sol-attn`（子参数 tau 0–4）/ `sla`（keep_percent 0.5–95）/ `vsa`（keep_percent） | sol-attn |
| start_percent | 0.0–1.0 | 0.2 |
| end_percent | 0.0–1.0 | 1.0 |
| dense_blocks | 字符串，如 `"0, 1, 47-49"` | `""` |
| min_tokens | INT 0–1<<20，step 512 | 12288 |
| extra_tokens | INT 0–256，step 64 | 256 |
| sink_conditioning | `exact_kv` / `exact_kv_and_rows` / `off`（H3 专用） | exact_kv_and_rows |
| verbose | BOOLEAN | false |

**修法**：按官方 input 顺序重写 `widgets_values`；判断不了语义就**全部落回官方默认值**（本例 UP 存的值本来就是这些默认值，只是错位）：

```python
["sol-attn", 1.3, 0.2, 1.0, "", 12288, 256, "exact_kv_and_rows", False]
```

- 节点在**子图**里时，改的是 `definitions.subgraphs[*].nodes`，不是顶层 `nodes`
- 改前备份原文件；改完按官方定义逐项校验区间/枚举（值域照源码 tooltip 抄）

**通用信号**：插件明明在、参数却报"值非法 / 超上限 / 空字符串转 INT 失败" → 先怀疑**版本间参数表迁移**，别逐条试值、别怀疑插件没装。

## 二、llama_cpp 加载失败 = conda 的 libstdc++ 太旧（不是没装）

```
RuntimeError: Failed to load shared library '.../llama_cpp/lib/libllama.so':
  /root/miniconda3/bin/../lib/libstdc++.so.6: version `GLIBCXX_3.4.30' not found
  (required by .../llama_cpp/lib/libggml-cuda.so.0)
```

`pip show llama-cpp-python` 显示已装（0.3.35）——问题在 **conda base 自带的 libstdc++ 是 GCC 11（只到 GLIBCXX_3.4.29）**，而 llama.cpp 的 CUDA 库要 GCC 12+ 的 `GLIBCXX_3.4.30`。

诊断（三行定性）：

```bash
strings /root/miniconda3/lib/libstdc++.so.6 | grep -o "GLIBCXX_3\.4\.[0-9]*" | sort -V | tail -2
strings /usr/lib/x86_64-linux-gnu/libstdc++.so.6 | grep -o "GLIBCXX_3\.4\.[0-9]*" | sort -V | tail -2
<venv>/bin/pip show llama-cpp-python | head -2
```

修（系统库已含 3.4.30 时最省事、可回滚）：

```bash
cp -a /root/miniconda3/lib/libstdc++.so.6 /root/miniconda3/lib/libstdc++.so.6.bak_$(date +%m%d)
ln -sf /usr/lib/x86_64-linux-gnu/libstdc++.so.6 /root/miniconda3/lib/libstdc++.so.6
<venv>/bin/python -c "import llama_cpp; print('OK', llama_cpp.__version__)"
```

备选（不改系统库）：`conda install -y -c conda-forge libstdcxx-ng`。

⚠️ **修完必须重启 ComfyUI**——Python 进程内的 .so 加载已失败，热改无效。

出处：llama-cpp-python discussion #2032、AskUbuntu / StackOverflow 同例（`ln -sf` 系统库 与 `conda install libstdcxx-ng` 两种标准解法）。

## 三、GLIBCXX 修好后的下一层：`不支持 Qwen35ChatHandler`

```
RuntimeError: 当前 llama-cpp-python 不支持 Qwen35ChatHandler，请更新 llama-cpp-python。
  comfyUI-llama-TE/nodes.py:702 _创建qwen35聊天处理器
```

**PyPI 的 `llama-cpp-python`（abetlen 原版）不支持 Qwen3.5+**：官方 issue **#2137「Support for Qwen 3.5 models」**（已关闭）里社区结论是改用 **JamePeng fork**；插件 README 也写着「`保留历史think` 仅**新版 Qwen35ChatHandler** 支持」。

**wheel 选名**（`JamePeng/llama-cpp-python` releases）：

- 平台 × CUDA × Python 三段都要对：`cp312` = Python 3.12，`linux_x86_64` = 云实例
- **Linux 只有 `cu131 / cu128 / cu126 / cu124` —— 没有 `cu130-linux`**（cu130 只有 Windows 版）→ 按「torch 是 cu130」手拼 `-cu130-linux-` 必然 404（本次踩过）
- 选版顺序：`cu131`（最接近 cu130）→ 不行退 `cu128`；文件形如 `llama_cpp_python-0.3.49+cu131-cp312-cp312-linux_x86_64.whl`
- 装法：先 `pip uninstall -y llama-cpp-python`，再 `pip install <URL>`（`+` 交给 pip 自己编码，别手动 `%2B`）

**铁律：tag 名和 asset 文件名一律从 API 抄，不手打**（连字符/大小版本极易错，一次手打错 = 一次 404 + 一轮返工）：

```bash
curl -s "https://api.github.com/repos/JamePeng/llama-cpp-python/releases?per_page=40" | python -c "
import sys,json
for r in json.load(sys.stdin):
    for a in r.get('assets',[]):
        if 'linux' in a['name'] and 'cp312' in a['name']:
            print(r['tag_name']); print('  ', a['browser_download_url'])
"
```

**验证装对没有**（不是看 pip 输出，是看 handler 在不在）：

```bash
<venv>/bin/python -c "
import llama_cpp, importlib
m=importlib.import_module('llama_cpp.llama_chat_format')
print('版本:', llama_cpp.__version__)
print([x for x in dir(m) if 'Qwen35' in x or 'Qwen3' in x])   # 期望含 Qwen35ChatHandler
"
```

## 四、KJNodes `MiniMaxH3MemoryEfficientSageAttentionPatch`：导入期符号探针

```
RuntimeError: sageattention is not new enough version or could not determine CUDA architecture,
cannot apply MiniMax H3 Memory Efficient Sage Attention Patch.
  ComfyUI-KJNodes/nodes/ltxv_nodes.py:2183
```

**报错条件（源码实证）**——节点在**模块导入期**做探针，任一步失败就**静默留 `None`**，直到跑图才炸：

```python
_cuda_archs = None
try:
    from sageattention.core import per_thread_int8_triton, per_warp_int8_cuda, \
        per_block_int8_triton, per_channel_fp8, get_cuda_arch_versions, attn_false
    _cuda_archs = get_cuda_arch_versions()
except Exception:
    pass
...
if _cuda_archs is None: raise RuntimeError("sageattention is not new enough version or ...")
```

**诊断（逐符号定位，不要只报"版本旧"）**：

```bash
<venv>/bin/pip show sageattention | head -2
<venv>/bin/python -c "
import importlib
m=importlib.import_module('sageattention.core')
for n in ['per_thread_int8_triton','per_warp_int8_cuda','per_block_int8_triton','per_channel_fp8','get_cuda_arch_versions','attn_false']:
    print(f'  {n}:', '有' if hasattr(m,n) else '缺')
"
<venv>/bin/python -c "import torch;print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"  # 5090 = (12,0) = sm120
```

**版本事实（2026-09 核实）**：

| 来源 | 6 个符号 |
|---|---|
| PyPI `sageattention`（最新就是 **1.0.6**） | 只有 `attn_false` ❌ |
| thu-ml/SageAttention **v2.2.0 tag** | 只有 `get_cuda_arch_versions` ❌ |
| thu-ml/SageAttention **main** | **6 个全有** ✅ |

→ KJNodes 要的是 **main 级**的 API，`pip install sageattention==2.2.0`（README 仍写着，但 **PyPI 已无 2.x**）也不够。

**首选出路：作者自己的预编译 whl** —— `huggingface.co/Kijai/PrecompiledWheels`（thu-ml issue #361 里被点名「older .whls by @kijai here」），有 `sageattention-2.1.0 / 2.1.1 / 2.2.0-cp312-cp312-linux_x86_64.whl`。装完**必须重跑上面的逐符号检查**确认 6 个齐全（该仓库 2.2.0 是作者自编、时间较早，与本环境 cu130 的加载兼容性未在本机跑完验证）。

```bash
<venv>/bin/pip install --force-reinstall --no-deps \
  "https://huggingface.co/Kijai/PrecompiledWheels/resolve/main/sageattention-2.2.0-cp312-cp312-linux_x86_64.whl"
```

**自己编译的两道坎（都撞过，别重复烧时间）**：

1. **torch 硬检查 nvcc 的 CUDA major 必须等于 torch 的 CUDA major**——`torch/utils/cpp_extension.py::_check_cuda_version` raise，**没有环境变量能跳过**：
   ```
   RuntimeError: ('The detected CUDA version (%s) mismatches the version that was used to compile
   PyTorch (%s)...', '12.8', '13.0')
   ```
   → 先装匹配的 nvcc（**只要 minor 大体同 major 即可过检查**）：
   ```bash
   . /etc/os-release; case "$ID-$VERSION_ID" in
     ubuntu-24.04) REPO=ubuntu2404;; ubuntu-22.04) REPO=ubuntu2204;; debian-12) REPO=debian12;; *) REPO=ubuntu2404;; esac
   curl -fsSL -o /tmp/cuda-keyring.deb "https://developer.download.nvidia.com/compute/cuda/repos/$REPO/x86_64/cuda-keyring_1.1-1_all.deb" \
    && dpkg -i /tmp/cuda-keyring.deb && apt-get update -qq \
    && apt-get install -y --no-install-recommends cuda-nvcc-13-0 cuda-cudart-dev-13-0
   /usr/local/cuda-13.0/bin/nvcc --version | tail -2
   ```
   编译时 `export CUDA_HOME=/usr/local/cuda-13.0; export PATH=$CUDA_HOME/bin:$PATH; export TORCH_CUDA_ARCH_LIST="12.0"`（sm120）。
2. **nvcc 对上后 thu-ml main 仍编不过 torch 2.14**：`csrc/qattn/pybind_sm80.cpp` 链上 `ATen/ExpandUtils.h:470: error: 'sizes' is not a member of 'at::symint'`（旧 symint API 被移除）→ **源码编译路线当前是堵死的**，别在原地重试；社区出路就是预编译 whl（kijai 的包，或 thu-ml issue #361 里 fat-tire 的 Dockerfile 编译方案）。

**备选（实在装不上时）**：该节点官方描述是 `EXPERIMENTAL ... reduce peak VRAM usage`，属**省显存的可选补丁**——旁路它（`Ctrl+B` / 改线让 `MiniMaxH3SigmaShift` 直连 `ModelAttentionBackend`）工作流照样能跑，代价是显存峰值升高，且**偏离 UP 标准版**（凡哥要求「不增加不减少」时不要擅自改，先报备由他定）。
