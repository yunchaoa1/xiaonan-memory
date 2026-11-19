# H3 Ref2VA 出片纪律：让参考图真的生效（2026-11-19 本机实测，43 秒成片跑通）

> 场景：手上已有分镜写好的 H3 六段式提示词 + 一套角色/场景/道具参考图，
> 要 ComfyUI 真跑出片子，且**人物、道具必须跟参考图一致**。
> 这份文档只讲「为什么画出来不是那个人」和「怎么修」，工作流转换本身见
> `references/ui-to-api-headless-submission.md`。

---

## 一、四条纪律（每条都对应一次真跑失败）

### 1. `mode` 必须显式写 `ref2va`，**永远不要留给 `auto`**

`MiniMaxH3UnifiedToVideo` 的 `mode` 可选：`['auto', 't2va', 'fl2va', 'ref2va']`。

**实测**：写 `auto` 时它判成了**纯文本生成** → 五张参考图一张都没用上 →
画面里只有提示词里"坐着喝茶的男人"，女主**完全没出现**，道具变成马克杯，质感是写实照片。
节点**不报错、不警告**，一路 success。

写死 `ref2va` 后，同一份提示词、同一套图 → 女主出现了、白瓷盖杯对了。

**推论**：`auto` 判"有没有参考图"这件事不可靠，**凡是要用参考图就必须写死 `ref2va`**。
排查顺序永远是「先看 mode 是不是 ref2va」，再怀疑提示词。

### 2. 参考图必须先缩到长边 ≈1024，**别把原图直接喂**

原图 2848×1600、各 4.5MB，五张 = 22MB 图像进显存 → 崩。
缩到 1024 宽、各 100KB → 同一份工作流同一套参数，四段连跑全 success。

**崩的样子**：`Fatal Python error: Aborted`，栈在
`vae.py:521 tiled_decode → _decode_pixels → forward`，**没有 Python ERROR 行**。
看到 `Aborted` 就去查参考图尺寸，别去调二采参数（详见 `ui-to-api-headless-submission.md` §11-bis）。

**做法**：出图前批量缩，一次搞定：
```python
from PIL import Image
im = Image.open(src); im.thumbnail((1024, 1024), Image.LANCZOS)
im.convert("RGB").save(dst, quality=92)
```
四视图（横）缩完约 1024×575，场景竖图约 768×1024 —— 这个量级 H3 认人够用。

### 3. 风格句必须写在 `detailed_description` **最前面**

同一份提示词，只差一句风格句，出来的东西完全两样：

| | 结果 |
|---|---|
| 没写风格句 | **写实电影感**，像实拍剧照，皮肤有毛孔、没有 CG 感 |
| 首行加 `Chinese 3D donghua animation film style, semi-realistic CG rendering, stylized character design, cinematic soft light.` | **半写实 3D CG**，皮肤有 CG 感、光影分层，接近国漫 |

**位置**：`detailed_description:` 字段的第一行，在 `[Shot 1]` 之前。
forest 的规则里本来就是「风格句 → 光位句 → 空气句 → 空间锚点句」，漏了第一句就是这个后果。

**注意**：加了风格句也只是"半写实 CG"，**还不是纯正国漫 3D**。要更偏国漫得继续调这一句，
它是唯一杠杆（H3 不认焦段/胶片/色温这些摄影参数）。

### 4. 一镜一个说话人，**别指望一帧两人都在说话**

实测成的四段里，段 02（林小满说话）画面只有她一个人、赵鹏在画外；
段 03（赵鹏说话）反过来。这是**对的** —— 回合制，符合 H3 的物理限制。

**别看到"画面里少一个人"就判定失败**，先回去看那一镜的提示词写的是谁在说。
真正的失败长这样：**该出现的主体从头到尾一次都没出现**（= 纪律 1 没做）。

---

## 二、绕开工作流里的提示词改写链（这是本项目最关键的一步）

很多 H3 工作流带一条"提示词优化"支路：
```
用户文本 → 媒体加载器 → 分流器 → QwenTE_ImageInfer（用 Qwen 32B 改写）→ Any Switch → 201.prompt
```
**我们写好的六段式会被它当"原始想法"重写成它自己的风格，终稿等于白写。**

### 正解：让 `201.prompt` 直接吃常量字符串

不要指望 `Any Switch` 的回落（那要看 bypass 状态，不稳）。**直接把整条支路从提交载荷里删掉**，
再把 `201` 的输入改死。本次实测有效的删除清单：

```python
for nid in ("1301",            # Any Switch
            "1379", "1380",    # QwenTE_ImageInfer + ModelLoader
            "1382", "1383", "1384", "1385", "1386", "1387",  # 5 条 system prompt + 另一个 Switch
            "220", "221",      # 媒体加载器 + 分流器
            "226",             # MiniMaxH3AudioLock
            "sg_1369", "sg_1371",   # 两个 BlockSparseAttention
            "1300", "1378"):        # ShowText，它们引用了被删节点的输出
    api.pop(nid, None)
```

删完之后要补的三处连线（**漏一处就断链**）：

```python
api["201"]["inputs"]["prompt"] = <六段式纯文本>        # 常量，不经任何节点
api["125"]["inputs"]["latent_image"] = ["201", 1]      # 采样器直接用 201 的 av_latent，跳过 AudioLock
api["1299"]["inputs"]["model"] = ["sg_1220", 0]        # Lora 直通，跳过 BlockSparse（一采）
api["1335"]["inputs"]["model"] = ["sg_1222", 0]        # 同上（二采）
```

**参考图不用 220/221**，改插普通 `LoadImage` 直连 `201`：
```python
api["9001"] = {"class_type": "LoadImage", "inputs": {"image": "s1.jpg", "upload": "image"}}
api["201"]["inputs"]["ref_images.ref_image_0"] = ["9001", 0]
```
`ref_images` 是 `COMFY_AUTOGROW_V3`（自动增长），`ref_image_0..N` 想接几张接几张。
**比跟 `media_state` 里那套 `"file": "minimax_h3/png [input]"` 命名纠缠省事得多。**

**代价**：删掉 audio lock 后就不能"锁参考音频音色"了；没参考音频时本来也没意义。
`226` 只负责在 latent 上做音频锁，删掉不影响出片（实测四段都有音轨、有台词）。

**副产品**：Qwen 32B 文本编码器不再加载，省显存也快。

---

## 三、节点参数的两个必坑

### `MinimaxH3LatentUpscaler3D` 的 `scale` 要写成 `mode.scale`

`mode` 是 `COMFY_DYNAMICCOMBO_V3`，**带子参数**。写 `"scale": 1.5` 会报
`required_input_missing / details: "scale" / extra_info.input_name: "mode.scale"`，
然后 `node_errors` 把 `1317` 标掉 → **二采整个被跳过，只出一采 960×544**（任务仍报 success，容易误判成跑通了）。

正确写法：
```python
api["1317"]["inputs"].update({
    "model_name": "minimax_h3_bf16_CONSERVATIVE_v5.safetensors",
    "mode": "scale by multiplier",
    "mode.scale": 1.5,
    "align": 32,
    "enable_temporal_chunking": True,
    "force_unload": True,
    "device": "cuda",
    "precision": "fp16",
})
```
**判据**：`node_errors` 非空但任务 success → **先去 `outputs` 数输出文件**，
少一个说明有支路被跳过（本例 `227` 一采在、`245` 二采不在）。

### 目录名大小写按 ComfyUI 报的来，别统一改

同一次提交里会同时报两种：
- `vae/minimax-h3/`（**小写**）→ `VAELoader` 的 `vae_name` 必须小写
- `diffusion_models/MiniMax-H3/`（**大写**）→ `UNETLoader`/`CLIPLoader` 必须大写

**别图省事全局 replace**，会按下葫芦起了瓢。**以报错里列的候选列表为准，逐个目录对。**

---

## 四、跑完之后的验证顺序

```
① status 是 success？         → 不是，先看日志末段（`Aborted` 见纪律 2）
② outputs 里有几个文件？       → 该有 2 个（227 一采 / 245 二采），少一个见 §三
③ 抽帧看人：首帧、每段中点、末帧 → 缺主体 = mode 没写 ref2va（纪律 1）
④ 看风格：是照片质感还是 CG     → 照片 = 缺风格句（纪律 3）
⑤ 看尾巴：最后 0.5 秒有没有崩   → 崩了看是否有定格句
⑥ 看穿帮：多手多脚、脸融、人穿模
```

抽帧注意：`cv2.imwrite` **不认 MSYS 的 `/d/...` 路径，会静默失败**（返回 False 但看不出错）。
一律用 `D:/...` 正斜杠路径，并检查返回值。

**拼多段**（本机 ffmpeg 不在 PATH，在 `/d/tools/ffmpeg/ffmpeg`）：
```bash
printf "file 'seg1.mp4'\nfile 'seg2.mp4'\n" > list.txt
/d/tools/ffmpeg/ffmpeg -y -v error -f concat -safe 0 -i list.txt -c copy out.mp4
```
同参数（同分辨率/帧率/编码）可以直接 `-c copy`，不用重编码。

**段长会比喂的秒数略长**：要 11 秒实际出 11.54，要 8 秒出 8.00 —— 都是 17n+5 帧格点的结果。
四段 11/13/10/8 拼出来 **43.37 秒**。

---

## 五、本次成立的基线（下次直接照抄，再动单变量）

| 项 | 值 |
|---|---|
| 画幅 | 16:9，一采 960×544，二采 1440×832（`scale=1.5`） |
| mode | **`ref2va`**（写死） |
| 参考图 | 5 张，长边 1024，各 ≈100KB，`LoadImage` 直连 |
| prompt | 六段式常量直塞 `201`，首行风格句 |
| 音频 | 无参考音频，删 audio lock 后仍正常出音轨 |
| 一采耗时 | ≈4.2–4.5 分钟／11 秒段 |
| 二采耗时 | ≈8 分钟（4 步 × ≈107 秒） |
| 四段 43 秒合计 | ≈45 分钟 |
