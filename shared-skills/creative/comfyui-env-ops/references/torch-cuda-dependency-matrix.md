# torch / CUDA / libstdc++ / wheel ABI 依赖矩阵（2026-09-10 云端实测）

环境基线：Ubuntu 22.04 / RTX 5090 (sm120) / Python 3.12.4(conda base) / venv `/home/waas/h3-0300/venv`
/ torch **2.14.0+cu130** / triton 3.8.0 / ComfyUI **0.35.0** / 驱动 590.44.01

## 1. GLIBCXX ↔ GCC 对照（选 libstdc++ 的依据）

| GLIBCXX 符号 | 由哪个 GCC 提供 |
|---|---|
| 3.4.29 | GCC 11（conda base 自带 / Ubuntu 22.04 原始） |
| 3.4.30 | GCC 12（Ubuntu 22.04 系统库上限） |
| **3.4.32** | **GCC 13** |
| 3.4.35 ~ 3.4.36 | GCC 15 ~ 16 |

读法：**报错要哪个号 = 那个 .so 是用哪个 GCC 编的**；要 ≥3.4.32 就必须上 conda-forge 新版（系统库无解）。

查当前库支持到哪：`strings <路径>/libstdc++.so.6 | grep -o "GLIBCXX_3\.[0-9]*\.[0-9]*" | sort -V | tail -3`

### libstdc++ 修法的两个坑（本 session 全部踩过）

1. **`libstdcxx-ng` 是空壳包**：conda-forge 的 `libstdcxx-ng-16.2.0-hdf11a46_4.tar.bz2` = **1545 字节、包内零文件**；
   `conda search --info` 显示 `dependencies: - libstdcxx 16.2.0 h934c35e_4` → 真文件在 **`libstdcxx`**。
   正确：`conda install -y -c conda-forge "libstdcxx>=16"` → 得到 `$PREFIX/lib/libstdc++.so.6.0.36` + `libstdc++.so.6` 软链。
2. **`--no-deps` 会拦掉实体包**（本次零文件的直接原因）。
   `conda install -y --no-deps libstdcxx-ng=16.2.0` → 事务全绿、`conda list` 显示 16.2.0，**但一个文件都没落地**。
3. **症状识别**：报错路径从 `/root/miniconda3/bin/../lib/libstdc++.so.6` 变成 `/lib/x86_64-linux-gnu/libstdc++.so.6`
   = 链接器回退到系统库了（conda 那份不存在），**不是新问题**。
4. 修好后的下一层立即出现：新编辑器编的 wheel 会要更高符号（本例 `3.4.30` → `3.4.32`）。

判包是否空壳（通用手法）：
```bash
curl -sL -o /tmp/p.tar.bz2 "https://conda.anaconda.org/conda-forge/linux-64/<包名-版本-build>.tar.bz2"
ls -la /tmp/p.tar.bz2 && tar -tjf /tmp/p.tar.bz2 | head    # 体积异常小 / 列表空 = meta 包
```

### 先删软链再装
若之前为应急做过 `ln -sf <系统库> $PREFIX/lib/libstdc++.so.6`，升级前必须 `rm -f` 该软链，否则 conda 不会覆盖。

## 2. torch 扩展编译：nvcc 必须与 torch 的 CUDA major 相同

`torch/utils/cpp_extension.py:_check_cuda_version` **硬性 raise，无环境变量可跳**：

```
RuntimeError: The detected CUDA version (12.8) mismatches the version that was used to compile PyTorch (13.0)
  ...  torch/utils/cpp_extension.py line 651, in _check_cuda_version
```

只看 **major**：torch cu130 → 装 CUDA **13.x** 的 nvcc 即可（13.0/13.2/13.3/13.4 都过）。

Ubuntu 22.04 只装编译器+运行头（几百 MB，不装完整 toolkit）：
```bash
. /etc/os-release; case "$ID-$VERSION_ID" in
  ubuntu-24.04) REPO=ubuntu2404;; ubuntu-22.04) REPO=ubuntu2204;; debian-12) REPO=debian12;; *) REPO=ubuntu2404;; esac
curl -fsSL -o /tmp/cuda-keyring.deb "https://developer.download.nvidia.com/compute/cuda/repos/$REPO/x86_64/cuda-keyring_1.1-1_all.deb" \
 && dpkg -i /tmp/cuda-keyring.deb && apt-get update -qq \
 && apt-get install -y --no-install-recommends cuda-nvcc-13-0 cuda-cudart-dev-13-0
/usr/local/cuda-13.0/bin/nvcc --version | tail -2     # 期望 release 13.0
```
编译时：`export CUDA_HOME=/usr/local/cuda-13.0 PATH=$CUDA_HOME/bin:$PATH`。
`setup.py` 读 `TORCH_CUDA_ARCH_LIST`（优先于 GPU 自动探测）→ 5090 用 `"12.0"`。

## 3. sageattention × torch：torch 2.13 移除了 wheel 依赖的符号

`MiniMaxH3MemoryEfficientSageAttentionPatch`（KJNodes）第三层报错（libstdc++ 修好后出现）：

```
ImportError: .../sageattention/_fused.cpython-312-x86_64-linux-gnu.so:
undefined symbol: _ZN3c104impl3cow23materialize_cow_storageERNS_11StorageImplE
```
demangle = `c10::impl::cow::materialize_cow_storage(c10::StorageImpl&)`

**PyTorch 官方 release notes（2.13.0）原文**：
> StorageImpl's built-in copy-on-write (COW) materialization is replaced by a pluggable materializer hook (#179063)
> …the friend `cow::materialize_cow_storage()` **have been removed**…
> It affects out-of-tree backends/extensions that called the removed StorageImpl COW symbols directly

→ kijai 的 wheel（`huggingface.co/Kijai/PrecompiledWheels`，2025-07 编，`sageattention-2.2.0-cp312-cp312-linux_x86_64.whl`）
在 torch **≥2.13 永久不可用**。**换 libstdc++ 后仍报这个符号 = 已进到下一层，不是修错了。**

已核实的"没有现成品"证据（别再重复搜）：
- `woct0rdho/SageAttention` releases 全是 `v2.2.0-windows.postN` → **只发 Windows，无 Linux**
- thu-ml/SageAttention 搜 torch 2.13/2.14 相关 issue = **0 命中**（上游未适配）；tags 仅 v2.0.1 / v2.2.0
- thu-ml 的 `v2.2.0` tag 的 `core.py` 缺 KJNodes 要的 5 个符号，**只有 main 分支 6 个全有**
- KJNodes 侧同类问题：issues **#736**（5070Ti/sm120，torch 2.9.1，`_qattn_sm89` 解析为 None）与 **#692**（5090），
  根因是"新 wheel 把算子注册在 `torch.ops.sageattention_qattn_sm89`"，KJNodes 的 `_resolve_qattn()` 只探模块属性 → 需给候选加 `getattr(torch.ops, f"sageattention_qattn_{arch}")`；两 issue **仍开着**、kijai 未回。
  注意：**那是"探测不到"层面**，与我们的"**.so 根本加载不了**（ABI）"不同层——即使有该 patch，torch 2.14 下仍加载失败。

## 4. 逐符号诊断（一条命令定性）

```bash
/home/waas/h3-0300/venv/bin/python -c "
import importlib, traceback
try:
    m = importlib.import_module('sageattention.core')
    for n in ['per_thread_int8_triton','per_warp_int8_cuda','per_block_int8_triton','per_channel_fp8','get_cuda_arch_versions','attn_false']:
        print(f'  {n}:', '有' if hasattr(m,n) else '缺 ❌')
    if hasattr(m,'get_cuda_arch_versions'):
        try: print('  get_cuda_arch_versions() ->', m.get_cuda_arch_versions())
        except Exception as e: print('  调用失败:', type(e).__name__, e)
except Exception:
    traceback.print_exc()
import sageattention; print('版本:', getattr(sageattention,'__version__','未知'))
"
```
KJNodes 侧判定逻辑（`ComfyUI-KJNodes/nodes/ltxv_nodes.py`）：模块级
```python
_cuda_archs = None
try:
    from sageattention.core import per_thread_int8_triton, per_warp_int8_cuda, per_block_int8_triton, \
                                  per_channel_fp8, get_cuda_arch_versions, attn_false
    _cuda_archs = get_cuda_arch_versions()
except Exception: pass
# execute(): if _cuda_archs is None: raise RuntimeError("sageattention is not new enough version or ...")
```
→ **报错文案只说明"探针失败"，不等于版本号问题**，必须逐符号跑上面的命令定位。

## 5. 该节点的可用出路

- 节点性质：KJNodes 自述 `EXPERIMENTAL!`，作用 = 把 H3 自注意力换成自定义 sageattention 内核以**降峰值显存**（非功能必需）
- 旁路：ComfyUI 选中节点按 **`Ctrl+B`**（rgthree/ComfyUI 旁路自动直通输入→输出，**不用改线**）
- ComfyUI 官方 docs（`docs.comfy.org/tutorials/video/minimax/minimax-h3`）也说明它可由启动参数 `--use-sage-attention` 替代
- ⚠️ `--use-sage-attention` 同样依赖可加载的 sageattention → 本环境**两条官方路都缺同一个件**
- 另有已知冲突：aimdo 0.5.x + sage/稀疏 = OOM（issues #16144 / #15759）
- 是否旁路属**需凡哥决策**事项（会偏离标准版 + 长视频显存风险）→ 摆事实给选项，别自己替他绕

## 6. 相关 issue / 来源

- PyTorch release notes v2.13.0（COW 移除 #179063）
- thu-ml/SageAttention issue **#361**（编译新 torch/python；评论区点名 `huggingface.co/Kijai/PrecompiledWheels`）
- kijai/ComfyUI-KJNodes issues **#736** / **#692**（sm120 上 `_qattn_sm89` 探测失败）
- abetlen/llama-cpp-python issue **#2137**（原版不支持 Qwen3.5 → 用 JamePeng fork）
- ComfyUI 官方 H3 教程：`docs.comfy.org/tutorials/video/minimax/minimax-h3`
