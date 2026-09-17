# SCAIL2 工作流排错

## SCAIL2ColoredMask 红色X

### 原因

SCAIL2ColoredMask 是 ComfyUI 原生核心节点（`comfy_extras/nodes_scail.py`），不是第三方插件节点。红色X通常不是真的缺失——是 ComfyUI Manager 误判。

### 排查步骤

1. **步骤1：点"放弃节点包"** → 重新加载工作流 `Ctrl+O`
2. **步骤2：检查ComfyUI版本**——SCAIL2ColoredMask需要v0.24+。v0.21以下没有这个节点
3. **步骤3：更新ComfyUI**——Manager → Update ComfyUI
   - 静默失败 = 非Git安装（便携版）。需手动更新
   - ⚠️ **不能只替换核心代码文件**——必须同时更新 `.venv` 里的Python包。代码和venv版本不匹配→ImportError崩溃
4. **步骤4：如已崩溃**——从旧版Git tag恢复文件（需匹配venv的pyvenv.cfg里的版本日期）

## 推荐工作流节点

不直接用 `SCAIL2ColoredMask`——用 SCAIL2-Easy 封装：

- **SCAIL-2 Simple Video**：主生成节点
- **SCAIL-2 Reference Pack**：多参考图打包
- **SCAIL-2 Fit Video**：驱动视频尺寸适配

模式选 `animation` 做动作迁移，选 `replacement` 做角色替换。

## 依赖模型清单

- SCAIL-2 模型：`Wan2.1/wan2.1_14B_SCAIL_2_fp8_scaled.safetensors`
- SAM3 跟踪模型：`sam3.1_multiplex_fp16.safetensors`（用于SAM3_VideoTrack节点）
- CLIP Vision：`clip_vision_h.safetensors`
- LoRA：`wan2.2 lora/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors`

## 教训：ComfyUI手动更新步骤

便携版（非Git安装）更新步骤：
1. `git clone --depth 1 <comfyui_url> ComfyUI_new`
2. 确认旧venv的pyvenv.cfg日期
3. `git log --before="<日期>" -1` 找到匹配commit
4. `git checkout <commit>`
5. 复制核心文件：execution.py, main.py, folder_paths.py, nodes.py, comfy/, comfy_extras/, comfy_api/
6. **不能只复制comfy/而忽略根目录Python文件**——execution.py导入的comfy_execution必须和代码版本一致
7. 备份原始文件再操作 — `cp -r comfy/ comfy.bak`
