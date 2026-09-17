# SVG 标记稿 → 多尺寸 PNG + 拼版自查 + 对比页（本机实测管线）

> 2026-09-11 天使OPC数字社区 logo 首战验证。**原生归属技能是 `logo-generator`**（该技能当前为用户所有、后台不可写），
> 故此处收录为跨技能可用的方法；凡哥执行 `hermes curator adopt logo-generator` 后，应把本文件迁回该技能并落在 `scripts/render_logo_set.py`。

## 本机渲染事实（实测）

- `cairosvg` **装了但渲染不了**：Windows 缺 `libcairo-2.dll`（报 `OSError: no library called "cairo-2" was found`）。
- 用 **`resvg-py`**：`pip install resvg-py`，自带二进制的 Rust 渲染器，无原生依赖，实测可用。
  调用签名：`resvg_py.svg_to_bytes(svg_string=<str>, width=<int>, height=<int>)` → PNG bytes。
- **中文**：SVG 里必须显式写 `font-family="Microsoft YaHei, 微软雅黑, Source Han Sans SC, sans-serif"`，否则渲染成豆腐块；微软雅黑实测正常。
- **透明背景**：SVG 里不画底色矩形，渲染出来就是透明（RGBA）。渲染后必须用 PIL 复核并报**实分辨率**。
- 保真度要求极高时兜底：本机 Chrome `--headless=new --screenshot --window-size=W,H <file:///url>`（中文路径要 `urllib.parse.quote`）。

## 一条命令出全套（脚本，见下方代码）

```bash
python scripts/render_logo_set.py --svg-dir <out>/svg --out-dir <out> \
       --color "#0052d9" --title "品牌名 · 图标方案"
```

产出：
- `png/<name>.png` 主尺寸 1024 透明
- `scale/<name>-64|32|16.png` 缩小实测（favicon 场景）
- `_contact_white.png` / `_contact_dark.png` 拼版 —— **交付前必须自己看**
- `showcase.html` 白底/深底/小尺寸对比页，每卡带 `data-hermes-send="我选 Xn，请按这个方向精修"` 按钮（点一下就直接回消息，用户不用打字）

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, glob, os
import resvg_py
from PIL import Image, ImageDraw, ImageFont

CN_FONT = r"C:\Windows\Fonts\msyh.ttc"

def render(svg_text, size):
    return bytes(resvg_py.svg_to_bytes(svg_string=svg_text, width=size, height=size))

def font(px):
    try:
        return ImageFont.truetype(CN_FONT, px)
    except OSError:
        return ImageFont.load_default()

def contact_sheet(items, bg, dest, cols=4, cell=300):
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * cell, rows * cell), bg)
    draw = ImageDraw.Draw(canvas)
    for i, (name, path) in enumerate(items):
        im = Image.open(path).convert("RGBA")
        im.thumbnail((int(cell * 0.72),) * 2, Image.LANCZOS)
        x = (i % cols) * cell + (cell - im.width) // 2
        y = (i // cols) * cell + (cell - im.height) // 2 - 10
        canvas.paste(im, (x, y), im)
        draw.text(((i % cols) * cell + 14, (i // cols) * cell + cell - 30), name,
                  fill=(255, 255, 255) if bg[0] < 128 else (40, 40, 40), font=font(22))
    canvas.save(dest)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--color", default="#0052d9")
    ap.add_argument("--title", default="图标方案")
    ap.add_argument("--main-size", type=int, default=1024)
    a = ap.parse_args()
    for sub in ("png", "scale"):
        os.makedirs(os.path.join(a.out_dir, sub), exist_ok=True)
    items = []
    for p in sorted(glob.glob(os.path.join(a.svg_dir, "*.svg"))):
        name = os.path.splitext(os.path.basename(p))[0]
        text = open(p, encoding="utf-8").read()
        main_png = os.path.join(a.out_dir, "png", name + ".png")
        open(main_png, "wb").write(render(text, a.main_size))
        for s in (64, 32, 16):
            open(os.path.join(a.out_dir, "scale", f"{name}-{s}.png"), "wb").write(render(text, s))
        im = Image.open(main_png)
        print(f"{name:10s} {im.size} {im.mode}")   # 报实分辨率 + 确认 RGBA 透明
        items.append((name, main_png))
    contact_sheet(items, (255, 255, 255), os.path.join(a.out_dir, "_contact_white.png"))
    contact_sheet(items, (10, 18, 34), os.path.join(a.out_dir, "_contact_dark.png"))
    # showcase.html 见 SKILL.md「对比页」说明，用相对路径引 png/ 与 scale/

if __name__ == "__main__":
    main()
```

## 不可跳过的质检纪律（首战血泪）

1. **产出后必须自己先看**：把 `_contact_white.png` 丢给 `vision_analyze`，逐稿问"形状是否完整对称、有无断裂/粘连/错位、缩到 16px 还认得出吗"。
   首战 7 稿里有 **4 稿是坏的**（像"上传"按钮、点阵散架、像虫子）—— 都是靠这一步在交付前拦下的。
2. **第一轮自查后重做再交付**，不要让用户替你做试错。
3. **深底版必看**：透明背景方案要同时验证白底和深底（如 `#0a1222`）两种场景。
4. **16px 必看**：细线、小点、密集点阵在 16px 会糊成一片 —— 那就不适合做 favicon。

## 渲染 / 交付补充坑（同项目后半程新增，均实测）

1. **裸路径数据 = 静默不渲染（最坑的一个）**：`<g>` 里必须写 `<path d="M … L …"/>`。
   把路径数据**裸写**进 `<g>`（`<g fill="none" stroke="…">M 44 34 L 50 25</g>`），resvg
   **不报错、直接忽略该元素** —— 实测表现为「整幅图只剩中心那个点」，白查半天。
   图形"不见了"第一个查这里。
2. **光学居中别手算**：渲染一版 → 读 alpha 包围盒 → 求内容中心与画布中心之差 →
   换算回 viewBox 单位（单位差 = 像素差 ÷ (渲染尺寸 ÷ viewBox 边长)）→
   把全部内容包一层 `<g transform="translate(dx dy)">` → 重渲染。实测一次纠掉「重心偏左 10 单位」。
   **多图层（错位叠印）必须按所有图层的并集取包围盒**，否则错位副本会把重心带偏。
3. **Chrome 无头截图的裁切坑**：`--window-size` 是**视口**，页面比它高就会被**裁掉**
   （曾因此漏看第三个方案段）。要全页就给足高度（如 `1200×6000`），或分段截。
4. **HTML 引图文件名不要带空格**：带空格极易 `src` 对不上 → 破图（本项目真实翻车一次）。
   中文路径一律 `"file:///" + urllib.parse.quote(path.replace("\\","/"))`。
5. **HTML 交付页也要先看再交**：渲染成 PNG 后丢 `vision_analyze`，核对「有没有破图 / 文字溢出 / 排版乱」。
6. **favicon 要单独放大标志占比**：色块底里按主标比例缩，16px 会小到看不见 →
   把色块内标志占比放大到约 **0.78** 重出小尺寸。
7. **从 GitHub 取技能文件（raw 域名不通时的兜底）**：`raw.githubusercontent.com` 解析不到时改走
   `https://api.github.com/repos/{owner}/{repo}/contents/{path}` → `json['content']` 是 base64，
   `base64.b64decode(...).decode('utf-8')` 即文件内容；整棵树用
   `/git/trees/{branch}?recursive=1` 筛 `type == 'blob'`；对比星数用 `/repos/{owner}/{repo}` 的
   `stargazers_count` / `forks_count` / `pushed_at`。
   ⚠️ 未认证 API 有速率限制：连续拉十几个文件会 `HTTP 403 rate limit exceeded`
   → 文件之间 `time.sleep(6)`，或分批取。
8. **命令行坑**：bash 里 `$TEMP` 展开成 MSYS 风格路径，**原生 Windows 程序（python / chrome）读不懂**
   → 给它们传 `D:/Temp/...` 这类原生路径。前台 `terminal` 超时上限 **600s**，批量渲染大图要分批。

## 交付目录规范（凡哥环境）

```
D:\数字资产\图片资产\logo-<品牌名>\
├── svg\         矢量源文件（改色/缩放无限清晰，是核心交付物）
├── png\         主尺寸透明 PNG
├── scale\       16/32/64 缩小实测
├── ai\          AI 生图线稿件（见 references/ai-generated-logo-marks.md）
├── showcase.html 对比页
└── _archive_*   被用户否掉的旧版本（换版即归档，别混在主目录）
```

**报路径时同时报实分辨率**；被否稿移到 `_archive_roundN/` 而不是留在主目录里混淆。
