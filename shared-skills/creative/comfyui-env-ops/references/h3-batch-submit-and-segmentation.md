# H3 批量提交与多段拼接（2026-11-22 《偏心》16 顆实测）

**场景**：剧本已拆完分镜，要一次性把十几二十顆排进 ComfyUI 队列跑成一条片子。
配套：`build_payload.py` + 自写的 submit 脚本。

---

## 一、`build_payload.build()` 四个硬坑

签名（`D:\Hermes\cache\build_payload.py`）：

```
build(prompt_text, duration, out_name, pics=None, w=960, h=544) -> str   # 返回的是 JSON 文件路径
```

**坑 1 · 返回路径不是 dict。**
```python
# ❌ ComfyUI 报 'str' object has no attribute 'items'
wf = build(text, dur, tag, pics=[("b1.jpg","b1.jpg")])
data = json.dumps({"prompt": wf})

# ✅
path = build(...)
wf = json.load(io.open(path, encoding="utf-8"))
data = json.dumps({"prompt": wf})
```
这个错报在 ComfyUI 端的 `apply_replacements`，前端只看到 500 Internal Server Error，不看 ComfyUI 进程日志根本找不到原因（真异常在 `for node_number, node_struct in prompt.items()`）。

**坑 2 · `pics` 是 `(目标名, 源名)` 元组列表。**
```python
pics=[("b1.jpg", "b1.jpg")]   # ✅ 目标名 = ComfyUI input 里的文件名
pics=[pic]                     # ❌ ValueError: too many values to unpack (expected 2)
```

**坑 3 · 默认横屏 960×544。竖屏必须显式传。**
```python
build(..., w=544, h=960)
```
不传就出横屏，构图全废，而且不报错。

**坑 4 · duration 上限 15.0，不是 15.08。**
帧数格点 `17n+5` 取最近合法值极易算出 362 帧 = 15.0833 秒：
```
value_bigger_than_max / duration / Value 15.083333333333334 bigger than max of 15
```
**单颗安全上限 = 345 帧 = 14.375 秒。** 362 帧必被拒。

常用格点：205→8.54s｜260→10.83s｜277→11.54s｜311→12.96s｜328→13.67s｜**345→14.38s（上限）**｜362→15.08s（超限）

---

## 二、一顆生成放多段（省时主力）

一颗 12–15 秒塞 **3–4 段**，每段一个主节拍，段间用 `Cut at X.Xs to:` 标切点：

```
the woman's eyes drift to the window at frame right, her head turning a few degrees, her hands still folded.
Cut at 3.9s to: the man on the left leans in, his forearms sliding forward on the table, his head tilting down toward her, his mouth opening.
Cut at 7.8s to: the woman lifts her head, meets his look, and answers calmly, her lips moving in short even movements.
```

- **段数上限 4。** 5 段起尾段会崩。
- **⛔ 绝不许跨场景。** 一顆里混两个空间，构图两边都不对，白跑。跨场景就拆成两颗。
  （本次事故：一颗把「咨询室沉默」和「老家妈收碗」塞一起，必须拆开重排。）
- 同场景多颗必须都用同一张参考图起，否则机位/景别会漂。

---

## 三、节拍表：台词秒数不许凭感觉给

**本机实测语速 3.7 字/秒**（edge-tts Xiaoxiao `rate=-8%`，562 字 / 152 秒）。

```
单镜秒数 = 台词字数 ÷ 3.7
无台词镜（沉默/空镜）= 动作给 2.0–3.0 秒
单镜 > 5.5 秒 → 拆（超长台词拆成同颗里的两段，不是拆成两颗）
一顆 = 连续几镜相加 ≤ 14.38 秒，段数 ≤ 4
```

**先算总时长再决定颗数**，别拉到一半发现装不下台词。
（本次事故：按「每颗 10 秒」拍脑袋拆 20 颗，只装下 36 句，剩 13 句最狠的没处放，**白跑 2 小时**。）

---

## 四、提交、监控、中止

```
POST /prompt              body {"prompt": <dict>}      ← 必须包这层
GET  /history/<pid>        status.status_str + outputs
GET  /queue                queue_running / queue_pending
POST /interrupt  {}        中断在跑的
POST /queue      {"clear": true}   清排队
GET  /system_stats         200 = 就绪
```

- 提交前必探活（ComfyUI 一天会被外部杀掉好几次）。
- 后台监控每 30 秒轮询一次 `/history`，完成即通知；**别一个 pid 一个 pid 等**。
- 中止要两个动作都做：`/interrupt` × 2–3 次 + `/queue {"clear":true}`，然后确认 `running 0 pending 0`。只清 queue 不停 interrupt，正在跑那颗还会占卡。

---

## 五、合成（画面 + 配音 + 字幕）

**画面**：每颗先统一 `scale=W:H:force_original_aspect_ratio=increase,crop=W:H,fps=24` 再 concat。
**景别会漂**（同场景不同颗，H3 有时半身有时全身），统一裁剪是唯一解法，提示词锁不死。

**配音按节拍表拼**：每句 `apad=whole_dur=<目标秒>,atrim=0:<目标秒>` 补齐再 `concat`，
让每句台词严格落在它那一镜的时间窗里，不越界压到下一镜。无台词镜塞 `anullsrc` 静音。

**字幕**：PIL 渲透明 PNG → `overlay=(W-w)/2:H*0.72:enable='between(t,t0,t1)'`，一层一个 enable。
三层颜色：她说=灰 `(200,200,200)`｜我说/旁白=白 `(255,255,255)`｜关键句=暖金 `(245,200,120)` + 字号加大。

**中文换行两条铁律**：
1. **按标点断，不按字数硬切** —— 硬切会出「是什 / 么时候」这种断词
2. **标点不落行首** —— 某行以 `，。：；！？、` 开头就把该标点挪到上一行末尾

**ffmpeg 只认 Windows 路径**：`D:/tools/ffmpeg/ffmpeg` + `D:/...`。`/d/...` 会静默失败（cv2 抽帧尤其明显，`int()` 拿到乱码才暴露）。

---

## 六、人物外观：别用纯黑剪影，用逆光半剪影（2026-11-22 对比实测）

想绕开「AI 画脸崩」时，第一反应是纯黑剪影 —— **实测不成立**：

| 做法 | 结果 |
|---|---|
| 纯黑剪影（只有轮廓） | H3 认不出性别，把一男一女画成两个男的；人物像棋子、没有情感 |
| **逆光半剪影**（侧脸轮廓＋发丝＋衣褶＋胡茬，但没有五官细节） | ✅ 身份稳、情绪到位、不崩脸 |

**逆光半剪影的写法**：单一暖光源在人物后侧（窗/门/走廊灯），人物整体压到接近黑，只留边缘光和轮廓线；衣服材质（针织开衫、衬衫领）要能看出来。
实测产出比纯剪影好一个档次 —— 它的情感靠**姿态**给（他前倾、她缩起来、头发往前垂），不靠脸。

**三条硬规矩：**
1. **性别/年龄/体型必须在生图阶段写死，不能指望 H3 补。** 图里是谁就是谁，文字写「一男一女」但图里是两个男人，H3 照图走。（原话：「图赢过文字」。）写法：`short tousled hair, broad shoulders, heavy jaw` / `hair falls to her shoulders, narrow shoulders, smaller frame`。
2. **童手/童身要专门写。** 只写「小女孩的手」会画出成年男人的手（大手、粗指、手臂有毛）；要写「儿童的手、小、肉乎乎、手指短、无毛、穿连衣裙袖口」。
3. **远/小主体只做空间，不做身份。** 小到一定程度 H3 补不出细节，那是系统级限制，任何提示词都修不好。

同一场景的每一颗都必须从**同一张参考图**起，否则机位和景别会漂（构图锁不住，只能后期统一裁剪）。

---

## 七、成本口径（RTX 5080 Laptop 16G，544×960 一采）

- 一颗 12–15 秒 / 3–4 段：**约 9–12 分钟**
- 3 分钟片子 ≈ 16 顆 ≈ **3 小时**
- 报时间给凡哥时按顆数算，别按「大概多久」拍
