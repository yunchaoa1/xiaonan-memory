# 剪影动画短片 · 完整生产配方（2026-11-22 实测）

**案例**：《偏心》84 秒情感内容短片（心理咨询式对话 + 童年闪回）。

**为什么用剪影**：情感内容要"有人演戏"，但 AI 生图的人物一致性扛不住 —— 剪影没有脸，绕开了这个死穴，而且自带距离感（观众会把自己的故事套进去）。

---

## 一、技术链路

```
agnes-image-2.1-flash 出剪影关键帧（10-16 秒/张）
        ↓ 缩到 1024 宽
H3 ref2va 竖屏 544×960（二采 832×1440），每颗 5.17 秒
        ↓
ffmpeg concat 拼接 + PIL 文字层 + 配音
```

### 生图调用（可直接复用）

```python
body = json.dumps({
    "model": "agnes-image-2.1-flash",
    "prompt": prompt,
    "size": "1024x1792",
    "n": 1,
}).encode()
req = urllib.request.Request(
    "https://apihub.agnes-ai.com/v1/images/generations",
    data=body,
    headers={"Content-Type": "application/json",
             "Authorization": "Bearer " + key},
)
# key 在 D:/Hermes/config.yaml 的 custom_providers.agnes.api_key
```

**并发 4 张 = 16 秒出齐。** 单张 10-16 秒。

❌ `gpt-image-2-medium` 单张 420 秒超时，多张分镜不要用。

---

## 二、8 张场景图的提示词（全部实测出图可用）

所有提示词统一带这几句：**黑白剪影动画风格 / 纯黑剪影 / 无面部细节 / 背景透光窗户 / 逆光勾边 / 极简 / 电影感 / 竖构图**。

### b1 心理咨询室（主场景，出现最多）

> 黑白剪影动画风格。一间安静的心理咨询室，两个人隔着一张矮桌对坐。镜头在人物侧面平视。**右边是一个女性**：深色长发垂到肩膀、搭在衬衫领子上，肩膀窄，手腕细，坐得笔直，两只小臂搭在桌面，双手松松交叠。**左边是一个男性**：短发，肩膀又宽又方，体型明显比她大，身体微微前倾，双手在桌上松松交扣。两人中间是一张矮桌。他们背后是一扇很高的窗户，窗外是明亮的天光，逆光把两个人勾成纯黑剪影。房间里没有别的光。极简构图，电影感，竖构图。

**关键**：性别必须写在最前面。第一次生图只写了"两个人隔桌对坐"，结果画成两个男人，后面 H3 全程照图走。

### b2 门口（闪回主场景）

> 黑白剪影动画风格。一间老房子的走廊，尽头是一扇开着的门。**一个矮小的孩子**（齐肩短发，七八岁的身形）站在门外，面向房间里，一动不动。门里透出暖色的光，能看见客厅里**两个大人的剪影**（一个偏高的男性、一个偏矮的女性），他们站得很远，轮廓被虚化。走廊这一侧是暗的，光全部从门里漏出来。极简构图，电影感，竖构图。

### b3 空椅子

> 黑白剪影动画风格。一张木桌，桌面上一只女人的手（手腕细、手指长）放在靠近镜头这一侧。桌子对面是一把空椅子，没有人坐，椅子上搭着一件外套。背景是透光的窗户，逆光勾出手和椅子的黑色轮廓。极简构图，电影感，竖构图。

### b4 另一组对话构图（备用）

> 黑白剪影动画风格。两个人坐在同一张桌子的相邻两侧（L 形），不是正面对坐。左边是男性短发宽肩，右边是女性长发窄肩。背后是透光的窗户。极简构图，电影感，竖构图。

### b5 餐桌推碗

> 黑白剪影动画风格。一张老式木质餐桌的桌面，镜头在桌面高度平视。画面左侧是一只手（女性，手腕细）正把一只陶瓷碗从自己面前推向桌子的右侧、推向画面的另一边。桌子右侧是空的，没有人。背景是昏暗的房间和一扇透光的窗户，逆光把手臂和碗勾成黑色剪影。碗正在滑动中。电影感，极简构图，竖构图。

### b6 水杯空镜

> 黑白剪影动画风格。一张木桌上放着一只玻璃水杯，镜头在桌面高度平视。窗外柔和的光从背后透进来，穿过杯身，杯子边缘发亮。杯里的水面有一层薄薄的反光。背景是模糊的窗框和暗淡的房间。画面里没有人物。极简，安静，电影感，竖构图。

### b7 手伸出去又缩回

> 黑白剪影动画风格。一只女性的手（手腕细、手指长）从画面左下方伸向画面右侧，伸到一半停住了，手指略微张开又收紧。手臂和手是纯黑色的剪影，背景是透光的窗户和昏暗的房间。这只手没有碰到任何东西，伸向的位置是空的。极简构图，电影感，竖构图。

### b8 行李箱

> 黑白剪影动画风格。地板上放着一个打开的行李箱，镜头在低处平视。一只女性的手正在把行李箱的拉链拉上，手停在拉链中间的位置。行李箱里隐约能看到叠好的衣物轮廓。背景是昏暗的卧室地面和一扇透光的窗户，逆光把行李箱和手勾成黑色剪影。极简构图，电影感，竖构图。

---

## 三、13 颗分镜表（84 秒）

**谈话是主体，回忆是插入。**

| # | 时间 | 秒 | 场景 | 动作 | 文案 |
|---|---|---|---|---|---|
| 1 | 0.0–4.2 | 4.2 | b1 | 女微微前倾开口，手抬起比划 | 她跟我说"我妈偏心我弟"的时候，我以为又是钱的事 |
| 2 | 4.8–10.7 | 6.0 | b2 | 孩子站门外不动，门里两个大人虚影转身 | 她说今年要结婚了，她妈说"你弟结婚早，钱花得差不多了" |
| 3 | 11.2–16.6 | 5.4 | b5 | 一只手把碗推向桌子另一边 | 她说这话语气特别平常，像在说今天天气不错 |
| 4 | 17.2–23.6 | 6.4 | b1 | 男前倾问，女抬头平静回答 | 我问她心里什么感觉 / 她说能理解啊 |
| 5 | 24.0–28.2 | 4.2 | b1 | 男再往前压，女手指在桌上蜷起 | 我说我没问你理解不理解 |
| 6 | 28.8–32.7 | 3.9 | b6 | 水杯水面微微晃 | 她停了一下，然后说有点说不上来 |
| 7 | 33.3–38.7 | 5.4 | b1 | 男问，女视线往下落 | 我问她有没有一次理直气壮跟家里要过东西 |
| 8 | 39.2–44.6 | 5.4 | b2 | 孩子站着，门里大人转身 | 她想很久，久到我以为她在敷衍我 |
| 9 | 45.3–49.3 | 4.0 | b1 | 女低头，长发滑落遮脸 | 我说不是好像，是没有 / 她不说话了 |
| 10 | 49.6–59.2 | 9.6 | b3 | 一只手在桌上，对面空椅两副碗筷 | 偏心最伤人的从来不是钱，是它教会你要东西这个动作本身是错的 |
| 11 | 59.2–67.5 | 8.3 | b7 | 手伸出去又缩回来 | 要一句准话先解释三遍 / 想要拥抱先说没事我不需要 |
| 12 | 67.5–77.1 | 9.6 | b8 | 手把行李箱拉链拉上 | 想被人留下，先替对方找好走的路 / 你以为你在懂事 |
| 13 | 77.1–83.1 | 6.0 | b1 | 女的头慢慢抬起，画面渐暗 | 那你呢 / 你上一次理直气壮要东西是什么时候 |

⚠️ 第 10、11、12 颗都超过 8 秒。**实测（2026-11-22）三颗都跑出来了**（实际 9.42 / 8.00 / 9.42 秒），但各自只塞了单一动作（扭头看空椅 / 手指张开再握拳 / 手按在拉好的箱子上）。**单动作能撑到 9 秒；要塞两三个动作仍按 C-5「5-7 秒一个回合」拆。**

---

## 四、H3 六段式模板（剪影专用）

```
subject_definitions:
<Subject 1> is the woman: dark hair falling to her shoulders and hanging free on both sides
of her face, narrow shoulders, a smaller frame than the man, sitting upright.
She sits on the right side of the table, in profile facing left toward the man.
<Subject 2> is the man: short tousled hair, broad heavy shoulders, a heavy jaw,
a larger frame than the woman, sitting with his body angled forward.
He sits on the left side of the table, in profile facing right toward her.

summary:
[reference generation] A monochrome silhouette animation. <Subject 1> sits facing
<Subject 2> across a low table and begins to speak; he listens without moving.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - shoulder-length dark hair,
narrow shoulders, smaller frame, upright seated posture in profile facing left.
<Subject 2> (appears in [Shot 1]): fully_preserved - short tousled hair, broad shoulders,
heavy jaw, larger frame, seated in profile facing right.
<Picture 1> (appears in [Shot 1]): fully_preserved - the tall window behind them,
the low table, the chairs and the direction of the light.

detailed_description:
Monochrome silhouette animation. Every figure and every object is a flat solid black shape
with no interior detail, no facial features and no highlights inside the body; the only light
is the bright window behind them and the soft falloff on the walls; graphic 2D animation
texture, heavy contrast between the pure black shapes and the pale window.

[Shot 1] The camera is locked in this single continuous shot throughout, no cuts,
holding the exact framing of <Picture 1>. Throughout the whole shot both figures keep
breathing: their shoulders rise and fall very slightly and their heads drift by a
millimetre or two.

<Subject 1> leans forward a little and begins to speak: her chin lifts slightly, her
shoulders come forward by a few centimetres, and one hand rises off the table and turns
outward as she talks, then settles back down.

overall_soundscape:
A quiet room with a faint low hum of the city far outside.

non_diegetic_music:
N/A
```

### 四条写法纪律（都是踩过的坑）

1. **人物特征每颗照抄，一个字不改** —— 尤其是"长发垂到肩膀""肩窄""体型比她大"
2. **不写"什么什么都不动"** —— `The table, the chairs and the wall do not move.` 会外溢，整颗镜头死掉；改成正面写"两人一直在呼吸"
3. **动作写关节走向，不写状态词** —— ❌ `slowly lowers her head` → ✅ `下巴朝锁骨方向往下走，脖子变短，肩线塌下去，两侧长发从背上滑到前面垂下来`
4. **`duration` 走 17n+5 格点** —— 124=5.17s / 158=6.58s / 192=8.00s

---

## 五、实测数据

| 项 | 数据 |
|---|---|
| 生图 | agnes-image-2.1-flash，10–16 秒/张，4 张并行 16 秒 |
| H3 一采 | 544×960，约 4.5 分钟 |
| H3 二采 | 832×1440，约 8 分钟 |
| 单颗总耗时 | ≈ 12 分钟 |
| 84 秒片（13 颗） | ≈ 2.6 小时 |

## 六、已验证 / 未验证

**整条片子已跑通**（2026-11-22）：13 颗全部 `success`，拼成 `D:/SDkecheng/ComfyUI/output/情感内容_偏心_剪影成片.mp4`，832×1440 / 83.79 秒 / 10MB。

**已验证**：
- 剪影质感在 H3 里全程保持（不变真人、不糊、不崩）
- 微动作可做（低头、塌肩、头发滑动、抬头、手指张开到握拳）
- 竖屏 832×1440 成片成立，不用先拍横屏再裁
- 性别在剪影里能保住 —— 前提是**生图时必须写清性别**（写 \"两个人隔桌对坐\" 会默认画成同性别）
- **「推碗」这类物件被手带着移动能做出来**：碗从桌面中间滑到右侧，手一直扣着碗沿跟着走，没有出现\"碗自己飘\"
- **跨镜头构图一致性过关**：同一张 b1 起的 s01 / s04 / s05，两人位置、大小、窗户位置完全一致，剪在一起不跳
- **闪回段落（b2）成立**：孩子站暗走廊、门里暖光下两个大人虚影，画面把\"被排除在外\"说完了

**仍未单独验证**：
- b2 里\"远处大人转过身\"这个动作是否真的执行了（抽的是 3.3 秒那一帧，只确认了构图和人物在场，没逐帧比对大人有没有转）
- b7 的\"手伸出去再缩回\"只有\"手指张开→握拳\"这段看得清，**手的位移（伸出去 / 缩回来）不明显**，实际成片靠\"张开变握拳\"承担叙事

---

## 七、成片合成配方（84 秒，实测）

```
ffmpeg concat 13 颗 → PIL 渲字幕层 + overlay enable='between(t,a,b)' → 丢原音轨、混入自己的配音
```

### ① 时间轴：按配音排，不足定格补

13 颗实测合计 **82.75 秒**，配音 **83.69 秒** —— 总差不到 1 秒，但**每颗跟它那句台词并不等长**，逐颗累计会错开（越往后越早）。处理：

- 每颗的起点对到它那句台词的起点
- 单颗比台词短 → 尾巴**定格补足**：`tpad=stop_mode=clone:stop_duration=N`
- ❌ **不要用 `setpts` 慢放补时长** —— 会把已经做对的微动作拖成慢动作

### ② 字幕：按标点断行、标点不落行首

按字数硬切会把「是什么时候」切成「是什 / 么时候」。`wrap_smart`（`D:/Hermes/cache/emotion/wraplib.py`）两步：

1. 先按 `，。：；！？、` 切成块，再按行宽装箱（放不下才硬切）
2. **行首标点搬到上一行末尾**（「，是错的」这种开头就要修）

**颜色分工**：白 = 我说的 / 灰 = 她说的 / 暖金 + 放大字号 = 关键句。

### ③ 落地文件

| 东西 | 路径 |
|---|---|
| 成片 | `D:/SDkecheng/ComfyUI/output/情感内容_偏心_剪影成片.mp4` |
| 合成脚本 | `D:/Hermes/cache/emotion/make_final2.py` |
| 断行脚本 | `D:/Hermes/cache/emotion/wraplib.py` |
| 分镜表 | `D:/Hermes/cache/emotion/分镜_偏心_13颗.md` |
| 场景图 | `D:/Hermes/cache/emotion/sil/b1.png ~ b8.png` |
| 13 颗原片 | `D:/SDkecheng/ComfyUI/output/Minimax_00017 ~ 00029-audio.mp4` |

**还缺的一样**：没有背景音乐（人声 + 画面撑情绪）。凡哥看片时未提，留作后续。
