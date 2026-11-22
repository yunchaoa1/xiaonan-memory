# 文字卡短视频合成配方（ffmpeg + PIL + whisper 对齐）

**场景**：把一段文案做成竖屏短视频（金句卡、情感内容、产品说明、片头片尾）。
不走扩散模型，纯「一张底图 + 文字图层 + 配音」合成。**2026-11-22 实测跑通**（21 秒 / 1080×1920 / 7 句 / exit 0）。

---

## 一、为什么不能用 `drawtext` 写中文（踩过的坑）

`drawtext` 在中文场景基本不可用，两个死结：

1. **`filter_complex` 里表达式内层的逗号会被当成分隔符**
   `alpha='if(lt(t,0.00),0,if(...))'` → 报 `Invalid argument`。转义链（`\,`、加引号、换单双引号）在 `subprocess` 传列表参数时尤其不可靠。
2. **`text` 里的换行 `\n` 在传参路径上不稳定**，多行中文排版几乎没法精确控制。

**正解：把文字用 PIL 渲染成透明 PNG，再用 `overlay` 叠上去。** 中文排版（字体/字号/行距/居中/阴影）完全可控，ffmpeg 只负责叠和时间控制。

---

## 二、完整配方

### 1. 用 PIL 生成文字层（每个时间段一张）

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT = r"C:/Windows/Fonts/msyhbd.ttc"   # 微软雅黑粗体
FS, LS, TOP = 66, 34, int(H * 0.15)     # 字号 / 行距 / 顶部起点

def make_layer(path, lines):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, FS)
    y = TOP
    for ln in lines:
        bbox = d.textbbox((0, 0), ln, font=font)
        x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0]   # 按实际墨迹居中，不是按宽度
        for dx, dy in [(3, 4), (2, 3), (1, 2)]:         # 多方向阴影，亮背景也可读
            d.text((x + dx, y + dy), ln, font=font, fill=(0, 0, 0, 200))
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255))
        y += FS + LS
    im.save(path)
```

**要点**：
- 居中要用 `textbbox` 的 `bbox[0]` 偏移修正，直接用 `(W - text_w) // 2` 会因为标点留白看起来偏。
- 阴影至少三层（3,4 / 2,3 / 1,2），单层在亮背景上糊。
- 一屏最多两行，每行 ≤12 个汉字（1080 宽 / 66 号字）。

### 2. 底图缓慢推近（Ken Burns）

```python
"[0:v]scale=1620:2880:force_original_aspect_ratio=increase,"
"zoompan=z='min(zoom+0.00032,1.16)':d=%d:"
"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
"eq=brightness=-0.05:contrast=1.05:saturation=0.93,setsar=1[base]" % int(DUR * 30)
```

- `z` 的增量 × 帧数 ≈ 总放大比例。`0.00032 × 636 帧 ≈ 1.20`，扣掉起步后约 1.16 倍。
- 单张图靠这一层就能撑 20 秒不闷。

### 3. 逐层 overlay（带时间窗）

```python
cur = "base"
for i, (st, en) in enumerate(windows):
    fc.append("[%s][%d:v]overlay=0:0:enable='between(t,%.2f,%.2f)'[v%d]"
              % (cur, i + 1, st, en, i + 1))
    cur = "v%d" % (i + 1)
fc.append("[%s]fade=t=in:st=0:d=0.8,fade=t=out:st=%.2f:d=0.9,format=yuv420p[vout]"
          % (cur, DUR - 0.9))
```

`between()` 只有两个逗号，是 `overlay` 支持的写法，不触发第一条那个转义地狱。

### 4. ★ 时间轴怎么对得准：用 whisper 转写配音拿时间戳

**不要手工估算每句话的时长。** 配音生成后，本地转写一遍，直接拿到每句的起止时间：

```python
from faster_whisper import WhisperModel
model = WhisperModel(r"D:/Hermes/models/faster-whisper-large-v3",
                     device="cuda", compute_type="float16")
segs, _ = model.transcribe(voice_mp3, language="zh", vad_filter=True)
for s in segs:
    print(s.start, s.end, s.text)     # 直接当文字层的窗口用
```

**这是本配方最省事的一步** —— 30 秒音频转写只要几秒，拿到的边界比人工卡点准得多。

拿到后给每个窗口留一点余量：文字比声音**早 0.1~0.2 秒出现**、**晚 0.25~0.4 秒消失**，读起来才不赶。

---

## 三、踩过的坑

| 现象 | 原因 | 修法 |
|---|---|---|
| `Invalid argument` + 大段 filter 串打印出来 | `drawtext` 的 `alpha` 表达式里逗号被当分隔符 | 放弃 `drawtext`，改 PIL 图层 + `overlay` |
| `Filter 'color:default' has output 0 (bg) unconnected` | 加了 `color=` 黑底源但没接到任何下游 | 删掉没用到的源；底图直接 `[0:v]` 走 |
| 文字位置看着偏 | 用了 `(W - text_w) // 2`，没扣 `bbox[0]` | 用 `textbbox` 的实际墨迹宽度和偏移 |
| 亮背景上文字读不清 | 只有一层阴影 | 三层阴影（3,4 / 2,3 / 1,2） |
| 一句太长排不下 | 一行塞了 20 多个字 | 一句拆两行，每行 ≤12 汉字 |

---

## 四、能力边界（别夸大）

这条路做的是**「一张底图 + 文字节奏」**，能做：

- 金句卡、观点卡、情感内容、产品说明、片头片尾字卡

做不了（要另找工具）：

- 多镜头切换、画面转场、图形动效、数据可视化动画

**量级参考**：单张 2160×3840 底图 + 21 秒 / 7 句文字层，ffmpeg 合成约 20 秒；素材图另算（图片生成另计，可能几分钟一张）。

---

## 五、配合什么用

- **文案**先按内容结构写（钩子 → 共鸣 → 转折 → 翻译 → 落点），再拆成句
- **配音**走 `text_to_speech`（edge provider，`zh-CN-XiaoxiaoNeural`）
- **多图升级**：底图可以每句换一张，overlay 的 `enable` 窗口错开即可，配方不变
