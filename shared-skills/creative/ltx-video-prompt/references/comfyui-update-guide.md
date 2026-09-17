# ComfyUI 更新指南

## 更新前提

凡哥的ComfyUI使用 `uv` 管理Python环境。代码和venv必须同步更新。

## 正确更新步骤

1. Git化安装：
```bash
cd D:\SDkecheng\ComfyUI
git init
git remote add origin https://github.com/comfyanonymous/ComfyUI.git
git fetch --depth 1 origin master
git reset --hard FETCH_HEAD
```

2. 关闭所有ComfyUI进程：
```bash
taskkill /f /im python.exe
```

3. 更新venv：
```bash
uv sync
```

4. 补漏缺包：
```bash
uv pip install psutil
```

## 常见错误

### ImportError: cannot import name RAM_CACHE_LARGE_INTERMEDIATE
原因：只更新了代码文件没更新venv。解决方案：执行上面完整步骤。

### 拒绝访问 (os error 5)
原因：ComfyUI还在运行。解决方案：任务管理器结束所有python.exe。

### uv sync只解析1个包
原因：pyproject.toml被git重置为新版。正常现象——所有依赖都会重新同步。

## SCAIL2ColoredMask 红色X

SCAIL2ColoredMask是ComfyUI原生核心节点（`comfy_extras/nodes_scail.py`），不是自定义节点。
红色X = ComfyUI Manager版本检测误判。

解决：
1. ComfyUI界面中点"放弃节点包"
2. Ctrl+A → Delete → Ctrl+O 重新加载工作流
3. 若仍红X → ComfyUI版本太旧（需v0.24+），手动更新

SCAIL2-Easy封装方案（推荐）：
- SCAIL-2 Fit Video → 预处理视频尺寸
- SCAIL-2 Reference Pack → 打包多张参考图
- SCAIL-2 Simple Video → 主生成节点（animation/replacement模式）
