#!/usr/bin/env python3
"""扫描一个 ComfyUI 自定义节点目录，列出"真正缺失"的第三方 Python 模块。

为什么需要它：插件的 requirements.txt 常常漏包（LayerStyle 连缺 skimage /
blend_modes / blind_watermark / wget 四轮），一轮一轮试 pip install 极慢。
本脚本静态扫描目录内所有 .py 的 import 语句，与标准库、目录内本地模块、
ComfyUI 运行时模块比对，一次列全缺的包。

用法（云端 venv，在插件目录里跑）：
    cd /home/waas/h3-0300/ComfyUI/custom_nodes/ComfyUI_LayerStyle
    /home/waas/h3-0300/venv/bin/python scan_missing_node_imports.py

输出示例：
    还缺: ['blind_watermark', 'wget']
    还缺: 无 ✅

坑（已内置处理）：
- comfy / folder_paths / nodes / node_helpers 属 ComfyUI 运行时模块，在
  custom_nodes 目录里跑 python 时找不到是正常的——已在 COMFY_RUNTIME 排除，
  不要照单去 pip 装。
- 模块名 != pip 包名，装的时候要换算：
  skimage -> scikit-image, blend_modes -> blend-modes, cv2 -> opencv-python,
  blind_watermark -> blind-watermark, wget -> wget
- 装完先 `python -c "import X, Y; print('OK')"` 单测 import 再重启 ComfyUI，
  省一轮几十秒的启动时间。
"""
import importlib.util
import pathlib
import re
import sys

# ComfyUI 运行时模块：从 custom_nodes 目录跑 python 时找不到属正常，勿装
COMFY_RUNTIME = {
    "comfy",
    "folder_paths",
    "nodes",
    "node_helpers",
    "execution",
    "comfy_api",
}

IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", re.M)


def scan(root="."):
    root = pathlib.Path(root)
    mods = set()
    for p in root.rglob("*.py"):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        mods.update(IMPORT_RE.findall(text))

    std = set(sys.stdlib_module_names)
    local = {p.stem for p in root.rglob("*.py")} | {
        d.name for d in root.iterdir() if d.is_dir()
    }

    missing = []
    for m in sorted(mods):
        if m in std or m in local or m in COMFY_RUNTIME:
            continue
        try:
            if importlib.util.find_spec(m) is None:
                missing.append(m)
        except (ImportError, ValueError, ModuleNotFoundError):
            # 父包缺失等情况一律当缺处理
            missing.append(m)
    return missing


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    missing = scan(target)
    print("还缺:", missing if missing else "无 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
