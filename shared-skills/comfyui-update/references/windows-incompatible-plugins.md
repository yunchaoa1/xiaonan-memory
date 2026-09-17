# ComfyUI Windows不兼容插件清单

> 以下插件在Windows上无法安装依赖——直接删除插件目录即可。
> **⚠️ triton 例外**：官方无 Windows wheel，但 PyPI `triton-windows` 社区版可修复（见 SKILL.md「Windows Triton 修复」节）。因此依赖 triton 的插件（如 SolAttn、sageattention）装好 triton-windows 后可正常使用，**不要删**。

| 插件 | 不兼容的包 | 原因 |
|------|------|------|
| ~~flashvsr_ultra_fast~~ | ~~triton~~ | **已可修复**：装 triton-windows（见 SKILL.md） |
| comfyui-rtx-simple | NVIDIA RTX Remix SDK | 需要额外SDK |
| ComfyUI-RTX-Remix | OpenEXR、NVIDIA SDK | C++编译依赖 |
| CharacterFaceSwap | dlib | Windows上编译失败 |
| comfyui_custom_nodes_alekpet | 特殊依赖 | 未知依赖 |
| comfyui_layerstyle | inference-gpu | Linux专属 |
| ComfyUI_LayerStyle_Advance | inference-gpu | Linux专属 |

## 仅部分节点可用的插件

| 插件 | 缺失功能 | 原因 |
|------|------|------|
| ComfyUI-RVC | fairseq、torchcrepe | Windows编译失败，其他节点可用 |
| comfyui_faceanalysis | dlib | 人脸检测不可用，其他节点可用 |
