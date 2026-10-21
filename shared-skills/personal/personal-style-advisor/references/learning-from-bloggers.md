# 从短视频博主学方法论：抓取 → 转写 → 提炼

> 2026-10-20 实测走通（小红书 @侃哥讲男生穿搭，9 条口播全下全转）。
> 抓取反爬细节看 `camoufox-antidetect`；这里是**内容拿到手之后**的工序。

---

## 一、先判断博主值不值得学

按这个顺序筛，**身材/处境像不像**排第一（瘦高型博主的技巧套到微胖人身上会反向失效）：

1. 身材像不像（体重/身高量级）
2. 讲不讲底层逻辑（讲公式 vs 只发搭配图）
3. 是不是卖货号（主页写"同款看橱窗/收藏"＝有利益，只取逻辑）
4. 内容是否对他的处境有效（例：北方秋冬大衣内容，对海口完全无效）

## 二、干货号的正文往往不在文字里

实测：页面 `#detail-desc` 只有 hashtag，正文全在**视频**里（真人口播 + 画面大字幕）。
→ 别指望抓文字，直接走下载 + 转写。

## 三、取视频直链

详情页 `<video>` 是 `blob:`，下不了。真实地址：

```python
urls = page.evaluate("""() => performance.getEntriesByType('resource')
    .map(e => e.name).filter(u => u.includes('sns-video') || u.includes('.mp4'))""")
```

- 形如 `https://sns-video-qc.xhscdn.com/stream/.../xxx_258.mp4?sign=...&t=...`，**带时效签名**
- 也可用 `page.on("response")` 抓 `content-type: video/mp4`
- ⚠️ 不是每篇都有视频，图文笔记拿不到 mp4，要单独标"可能是图文"

## 四、下载

```bash
curl -sL -A "Mozilla/5.0 ... Firefox/156.0" -e "https://www.xiaohongshu.com/" -o <note_id>.mp4 "<直链>"
```

**必须带 Referer**。文件按 `note_id` 命名，转写稿靠这个对应回标题。

## 五、转写（本地 large-v3，不花钱，不上传别人服务器）

```
ffmpeg -y -v error -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out_16k.wav
```

- ffmpeg：`D:\tools\ffmpeg\ffmpeg.exe`
- 模型：`D:\Hermes\models\faster-whisper-large-v3`（`faster_whisper 1.2.1`，在 Hermes venv）
- 参数：`WhisperModel(model, device="cuda", compute_type="float16")` → `transcribe(wav, language="zh", beam_size=5, vad_filter=True)`
- **`initial_prompt` 塞领域词**能显著减少同音错词（穿搭场景塞"正肩 落肩 克重 版型 微胖 阔腿裤 工装裤"）
- 实测速度 **≈2.2× 实时**（60s 视频约 27s）
- 逐条落盘（.txt 带时间戳 + .json 分段），断了不丢

## 六、脚本位置（双机注意）

本机：`D:\Hermes\scripts\xhs_videos_batch.py`、`xhs_transcribe.py`、`xhs_blogger_notes2.py`、`xhs_status_probe.py`

⚠️ 脚本在 `D:\Hermes\scripts\`，**不在技能目录 → 技能会同步到另一台电脑，脚本不会**。换机要么拷，要么按本文参数重写。

## 七、提炼的诚实边界（凡哥最在意这条）

- 转写**一定有同音错词**（实测 9 条里 8 处）→ **逐条标"存疑"，不替它编圆**
- 卖货号的单品推荐**带利益** → 只取公式和避雷
- **反话型内容不能当规矩用**（"别跟我搜一样，怕你太帅"）→ 要点出来
- 男性博主讲"女生讨厌什么"是**转述**，标"女性视角未验证"
- 提炼稿按 `[侃]`（原话）/`[推]`（我推的）/`[待验证]` 三档标注来源
