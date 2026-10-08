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

**⚠️ Kijai 的 whl 在 cu130 环境不可用（2026-10-08 云端实测 ❌）**：`huggingface.co/Kijai/PrecompiledWheels` 的 `sageattention-2.2.0-cp312-cp312-linux_x86_64.whl`（13.9MB，hf-mirror 好下）装完 **import 即炸**：

```
ImportError: libcudart.so.12: cannot open shared object file: No such file or directory
  sageattention/quant.py:20 in from . import _fused
```

它是 **CUDA 12.x 编的**，cu130 环境只有 `libcudart.so.13`（torch 自带）→ 库对不上，符号再齐也白搭。（技能里那句"兼容性未验证"至此结案：**不可用**。）

**符号齐全的候选：`snw35/sageattention-wheel` 的 `+cu13` 版（2026-10-08 云端实测：6 符号全 True —— 但运行时仍崩，见本节末尾「血坑」；⚠️ 标签已从「正解」降级）**：

```bash
# GitHub release 直连被限速（实测 1.2KB/s），前缀套 ghfast.top（实测 3.3MB/s）
cd /root && curl -L --fail --retry 3 -o "sageattention-2.2.0+cu13-cp312-cp312-linux_x86_64.whl" \
  "https://ghfast.top/https://github.com/snw35/sageattention-wheel/releases/download/cu12-2.2.0-cu13-2.2.0/sageattention-2.2.0%2Bcu13-cp312-cp312-linux_x86_64.whl"
<venv>/bin/pip install -i https://pypi.org/simple --force-reinstall --no-deps "./sageattention-2.2.0+cu13-cp312-cp312-linux_x86_64.whl"
# 装完必跑上面的逐符号检查：6 个全 True 才算过；然后重启 ComfyUI（探针在导入期）
```

同仓库还有 `+cu12` 版（cu12 环境用）。备选 `pixeloven/SageAttention-Wheels`：`+cu130.torch2.13.0.sm120`（14MB，专为 5090 算力编，但 torch 2.13 编的，本环境 torch 2.12.1 未测）。

**选版纪律（照这个顺序，别再试错）**：① 先看 whl 的 **CUDA 标签**与环境 torch 的 CUDA major 对齐（cu130 环境要 `+cu13` 编的，`+cu12` 一定崩 libcudart）；② 再看 torch 版本接近度；③ 装完**逐符号探针**，6 个全 True 才重启。

### ⚠️ 血坑（2026-10-08 云端实测）：符号全 True ≠ 能用，还要过 ABI / torch 版本这关

上面那个 `snw35` 的 `+cu13` whl，在 **torch 2.12.1+cu130** 上：**import 正常、6 符号全 True、探针全过 —— 但工作流一跑就炸**：

```
RuntimeError: Tensor input must be on CUDA
  sageattention/quant.py:172 in per_warp_int8 → _fused.quant_per_warp_int8_cuda(q, q_int8, q_scale, ...)
```

**诊断办法（关键：先在 ComfyUI 之外做隔离测试，10 秒定性，别在 ComfyUI 里逐层猜）**：

```bash
cd <ComfyUI> && <venv>/bin/python - <<'PY'
import torch, sageattention
print("torch:", torch.__version__, "| torch.cuda:", torch.version.cuda)
from sageattention.quant import per_warp_int8
q = torch.randn(1, 4096, 16, 64, device="cuda", dtype=torch.bfloat16)
k = torch.randn(1, 4096, 16, 64, device="cuda", dtype=torch.bfloat16)
try:
    o = per_warp_int8(q, k, km=k.mean(dim=1, keepdim=True), tensor_layout="NHD", BLKQ=128, WARPQ=32, BLKK=64)
    print(">>> SAGE OK", o[0].device)
except Exception as e:
    print(">>> SAGE FAILED:", type(e).__name__, e)
PY
```

- **报 `SAGE FAILED`** → 是 **whl 与 torch 的 ABI 不匹配**，与 ComfyUI、工作流、插件补丁**全无关系**（本次就栽在这，在 ComfyUI 里白绕了 5 轮）；
- **报 `SAGE OK`** → 才轮到怀疑 ComfyUI 的显存机制（DynamicVRAM / async offload）。

**症状对照**：Python 层 `q.device.type == "cuda"` 为真（打在函数头的 `[ZZ_DEV]` 调试补丁**一行都不打印**），C++ 层却报 "must be on CUDA" → 这就是 ABI 版本错配的典型长相。**别再去搬张量、别改工作流**，那都是治不了病的。

**结论/纪律**：whl 选择不只看 CUDA major，**更看 torch 主版本** —— sageattention 的 C++ 扩展必须与运行环境的 torch 精确对齐。预编译轮子**名字里没标 torch 版本时**（snw35 的 `+cu13` 就没标），**默认它是为发布当时的 torch 编的，跨大版本（如 2.8→2.12）不可信**。对照：Kijai 的 whl 发布于 2025-07（torch 2.8 时代），本机是 torch 2.12 —— 跨了 4 个大版本。

**就地编译：本环境实测也失败（2026-10-08，别再原地烧时间）** —— 用当前 venv 的 torch 编（`--no-build-isolation`，理论上 ABI 对齐的正解）确实跑起来了，但 **wheel 没编出来**：`_fused` 编译单元成功（ptxas 全按 sm120 编完），随后另一个 nvcc 调用 `failed with exit code 1`，**整个 pip 事务回滚**（`Failed to build sageattention`）。日志里**连一行标准 `error:` 都没有**（只有汇总行）→ 最可能是模板展开吃爆内存、编译器进程被 kill。源码获取用 codeload 官方源最快、且云上真能通：

```bash
# 1) 源码（GitHub 直连在云上会被限速，套镜像；codeload 官方源实测最快）
cd /root && for U in "https://codeload.github.com/thu-ml/SageAttention/tar.gz/refs/tags/v2.2.0" \
  "https://ghproxy.net/https://github.com/thu-ml/SageAttention/archive/refs/tags/v2.2.0.tar.gz" \
  "https://gh-proxy.com/https://github.com/thu-ml/SageAttention/archive/refs/tags/v2.2.0.tar.gz"; do
  curl -L --max-time 90 --connect-timeout 10 -o /root/sage.tar.gz "$U"
  [ -s /root/sage.tar.gz ] && tar tzf /root/sage.tar.gz >/dev/null 2>&1 && break; rm -f /root/sage.tar.gz
done
tar xzf /root/sage.tar.gz && mv SageAttention-2.2.0 SageAttention
# 2) 编译必须--no-build-isolation（= 用当前 venv 的 torch 编，这才是 ABI 对齐的关键）+ 只编 sm120
cd /root/SageAttention && nohup env TORCH_CUDA_ARCH_LIST="12.0" MAX_JOBS=4 \
  <venv>/bin/pip install . --no-build-isolation --force-reinstall --no-deps > /root/sage_build.log 2>&1 &
# 3) 编完必跑：逐符号探针 + 上面的隔离测试，两个都过才重启 ComfyUI
```

**✅ 已验证的出路：旁路该节点（2026-10-08 凡哥确认「工作流可以了」）** —— `Ctrl+B` 旁路，或把工作流 JSON 里对应节点的 `mode` 改成 `4`，工作流照常出片。叠加证据让这条路更划算：**该工作流的加速并不依赖它** —— 链路是 `MiniMaxH3SigmaShift → [sage补丁] → ModelAttentionBackend`(`pytorch attention`) `→ BlockSparseAttention`(`sol-attn`)，**Sol-Attn 才是加速主力**，sage 补丁只是"再省峰值显存"的可选件，旁路它不损失加速。

**⚠️ 与下面「自己编译的两道坎」的关系**：那两条撞的是 thu-ml **main** + **torch 2.14** 的 `at::symint` API 移除；本次走 **v2.2.0 tag + torch 2.12**，撞的是另一个坎（nvcc 崩、与 API 无关）。**两条路线都堵死了源码编译 —— 不要把它当默认解法。**

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

## 五、云端装 whl 的纪律（2026-10-08 实测踩坑，通用）

1. **whl 存盘必须保留原生文件名**——`name-version-python-abi-platform.whl` 少一个字段就被拒。改名成 `llama_cpp_h3.whl` → pip 报 `ERROR: llama_cpp_h3.whl is not a valid wheel filename.`（uv 同理 `Must have a Python tag`）。`curl -o` 时就写全名，中间过程文件另起名。
2. **GitHub release 直连会被限速**（实测 1.2KB/s，"173MB 剩 39 小时"），前缀 `https://ghfast.top/` 实测 **3.3MB/s**（52 秒下完 173MB）。多源自动挑（卡死的源 15 秒自动让位）：
   ```bash
   U="https://github.com/OWNER/REPO/releases/download/TAG/FILE.whl"
   for P in "https://ghfast.top/" "https://gh-proxy.com/" "https://ghproxy.net/" "https://github.com/"; do
     rm -f f.whl; curl -L --connect-timeout 20 --speed-limit 102400 --speed-time 15 -o f.whl "$P$U"
     [ $(stat -c%s f.whl 2>/dev/null || echo 0) -gt 180000000 ] && break
   done
   ```
   HF 文件用 `https://hf-mirror.com/<repo>/resolve/main/<file>` 直连即可（实测 2.3MB/s）。
3. **装 whl 一律 `--force-reinstall --no-deps`**：版本号相同时（如 sageattention 都是 2.2.0、llama_cpp 都是 0.4.2）pip 会判定"已满足"直接跳过，必须 `--force-reinstall`；`--no-deps` 防它顺手动 torch/numpy（本次 llama_cpp 装依赖时给 venv 塞了 numpy 2.3.2——可接受，但要知道）。

## 六、llama.cpp 跑 CPU（`GPU offload available: no`）—— CUDA 后端没人去加载（2026-10-08 云上实测）

**症状**：`[comfyUI-llama-TE] llama.cpp GPU offload available: no` → "The model will run on CPU"（35B MoE 跑 CPU，一次提示词反推 ~4 分钟）。迷惑点：`libggml-cuda.so`(184MB) **就在** `llama_cpp/lib/` 里、`ldd` 依赖全解析、手动 `ctypes.CDLL` 也 OK —— **库没坏，是没人去加载它**。

**根因（源码级）**：ggml 的动态后端加载 `ggml_backend_load_all()` 只扫 **① 可执行文件目录 ② cwd**，**不认 `LD_LIBRARY_PATH`**（llama.cpp issue #17491 原话："CPU backends are only loaded if they are in the same directory as the executable"）。而 llama-cpp-python 的绑定**不自动调用它**，`libllama.so` 也不链接 CUDA 后端（`ldd` 只有 libggml.so / libggml-base.so）→ CUDA 后端永远躺着。

**诊断**：
```bash
ldd <venv>/lib/python3.12/site-packages/llama_cpp/lib/libllama.so | grep -iE "ggml|cuda"   # 确认没静态含 cuda
<venv>/bin/python -c "import llama_cpp; print([n for n in dir(llama_cpp) if 'backend' in n.lower()])"
# → 暴露的是 ggml_backend_load_all_from_path（注意：**没有** ggml_backend_load_all 这个名字）
```

**正确调法（三组对照实测）**：

| 调法 | 结果 |
|---|---|
| `load_all_from_path(None)`（走默认路径） | ❌ 注册后端数=0 |
| **`load_all_from_path(b'<venv>/lib/python3.12/site-packages/llama_cpp/lib')`** | ✅ **gpu_offload=True**，注册 CUDA+RPC+CPU 三个后端 |
| 先 `llama_backend_init()` 再 load | ❌ 0（**顺序不能反**） |

→ 必须**传明确的 lib 目录**（不能靠默认路径）+ **在 `llama_backend_init()` 之前**调用。光把 .so 软链到 exe 目录**不生效**（因为压根没人调 load_all）。

**固化：venv 级 `sitecustomize.py`**（`<venv>/lib/python3.12/site-packages/sitecustomize.py`，ComfyUI 零改动、随镜像走）：

```python
import sys
if any('main.py' in a for a in sys.argv):
    try:
        import torch      # ⚠️ 必须先 import torch！
        import llama_cpp
        llama_cpp.ggml_backend_load_all_from_path(b'<venv>/lib/python3.12/site-packages/llama_cpp/lib')
        llama_cpp.llama_backend_init()
    except Exception:
        pass
```

**⚠️ 血坑：不先 `import torch` 会让 ComfyUI 直接起不来**：
```
ImportError: .../torch/lib/libtorch_cuda.so: undefined symbol: ncclCommResume
```
llama 的 CUDA 后端抢在 torch 之前加载，会拽进一个**旧版 libnccl**；torch 随后加载 `libtorch_cuda.so` 就找不到 `ncclCommResume`（NCCL 2.19+ 符号）→ 启动失败（`exit 1`、端口 `http=000`）。**先 `import torch`** 让它占住自己的 nccl 即可。

**成功标志（启动日志）**：
```
ggml_cuda_init: found 1 CUDA devices (Total VRAM: 32111 MiB):
load_backend: loaded CUDA backend from .../libggml-cuda.so
load_backend: loaded RPC backend from .../libggml-rpc.so
load_backend: loaded CPU backend from .../libggml-cpu-sapphirerapids.so
```

**验证顺序纪律**：改 sitecustomize 后**先 `timeout 20 python main.py ...` 前台试跑**（`exit=124` = 20 秒没崩 = 成功），确认后再 `nohup` 转后台。别直接后台起——崩了只能看 `http=000`，浪费一轮。
