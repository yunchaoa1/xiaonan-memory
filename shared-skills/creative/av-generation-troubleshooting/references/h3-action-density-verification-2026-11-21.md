# H3 动作密度 · 词数真相 · 验收方法（2026-11-21 实测）

本文件是 `av-generation-troubleshooting` C-1 / C-5 / C-6 与「验收纪律」的原始依据。凡涉及「H3 一镜能写多少字」「动作为什么没做出来」「片子怎么验收」，以本文件为准。

---

## 一、词数口径：官方原文与来源核实

### 官方文件身份

`references/official/ref-en.txt`（下载自 AI-KSK/aiksk-minimax-h3-local-prompt）**不是民间经验，是 MiniMax 官方开源仓库文件**。

核实过程：
- 官方 GitHub：`MiniMax-AI/MiniMax-H3` → `skills/h3-prompt-writing/references/ref-en.txt`
- HuggingFace 同名仓库同一路径
- **两份 SHA256 前缀一致 `1e574f35`，23553 字节**
- AI-KSK 仓库里那份被改过（23894 字节，哈希 `b621067b`，多 341 字节）——**要原文用官方仓库那份**

### 官方原话（第 242 行）

> "For generation tasks, `detailed_description` is normally **350-500 English words**. Dialogue-dense content prioritizes fitting the complete spoken timeline rather than mechanically reaching word count."

> "Make `detailed_description` as detailed and explicit as possible. For each shot, clearly establish the current composition, subject appearance and position, environment and lighting, actions and state changes, camera movement, current sound, and the points where referenced content actually appears or takes effect. **Avoid reducing the description to a plot summary or a list of reference relationships.**"

### 关键辨析：这份文档是给「改写器」用的

文件名是《Full-Reference Mode **Rewrite** Output Format Guide》——**改写输出**格式指南。

官方管线：

```
人写的大白话 → Context-IR 改写器（云端托管）→ 六段式 → H3-Base 出片
```

- **Context-IR 是托管预处理系统，开源权重里没有**
- 官方说法：开源权重不含 Context-IR，「官方强烈建议接入管线或按 Prompting Guidance 自建等价预处理」
- **本地手写六段式喂 H3 = 手工模拟改写器的输出**

**所以 350-500 词是「改写器输出」的典型长度；本地手写达到这个详细度同样有效**（已实测，见第二节）。350-500 不是硬上限，是「写到这个量级才够详细」的意思。

---

## 二、对照实验：64 词 vs 516 词（同条件，唯一变量＝写法）

**条件全部相同**：同一段剧情（他绕过桌子推她肩膀）、5.17 秒／124 帧、同三张参考图（人物四视图 ×2 + 办公室）、同机位（40 度侧角手持锁定）、同风格句。

### 短版（64 词，动词式）

```
He rounds the desk corner toward <Subject 1> and plants one palm flat against her left shoulder.
Her shoulder is shoved back and she staggers half a step, her heel knocking the chair leg.
The desk and the chair stay where they are.
The movement stops and the picture holds still for the last second.
```

**结果**：手掌搭在肩上，她**笔直站着**、面带笑、双手垂着。画面读作「领导拍肩安慰」，**完全没有推力**。

### 长版（516 词，物理链式）关键段

```
His open palm travels along a clear, visible line and lands flat on the outer edge of her
left shoulder, just below the collarbone. The palm does not pass through her body.
The moment the palm lands, its forward pressure drives her whole upper body backward:
her left shoulder is pushed behind the line of her hips, her head tips back, and the
fabric of the grey cardigan bunches and creases around his hand.
Her weight transfers onto her back foot. She takes half a step backward, and her heel
strikes the base of the black mesh chair with a small recoil.
Her arms swing up loosely in front of her chest as she fights for balance.
```

**结果**：上身被推得后仰、眼睛紧闭眉头皱、双臂张开、**真的退开了半步**（3.6 秒位置明显比 2.8 秒靠后）。

### 结论

**同一颗镜、同一时长，516 词做的动作比 64 词多。词数不是限制器。**

另有：14.3 秒长镜写 **760 / 836 / 759 / 797 词**，四段全部跑通、零 node_errors、八拍动作做完。

---

## 三、动作物理链模板（可直接套用）

任何「肢体动作」都按这五段写，缺一段就退化成摆姿势：

| 段 | 写什么 | 反例 | 正例 |
|---|---|---|---|
| 1 出发 | 哪个部位动 | 「他推她」 | `his open palm` |
| 2 路径 | 沿一条看得见的线走 | （无） | `travels along a clear, visible line` |
| 3 落点 | 精确到身体部位 | `on her shoulder` | `the outer edge of her left shoulder, just below the collarbone` |
| 4 接触后果 | 受力方的几何变化 | `she is pushed back` | `her left shoulder is pushed behind the line of her hips, her head tips back` |
| 5 重心与恢复 | 位移量 + 稳身动作 | `she steps back` | `her weight transfers onto her back foot, heel strikes the chair base, arms swing up as she fights for balance` |

**辅助技巧：正向防穿帮**

H3 不画否定词。要防「手穿过身体」，用正向表述锚定：
> `The palm does not pass through her body.`
> `The redirected fist passes just outside his shoulder instead of passing through his body.`

（写成「手在肩膀表面上停住」这种正向动作描述，比写 `no clipping` 有效。）

---

## 四、57 秒长片逐段体检（4 段 × 14.3 秒）

**结构**：段01 对质→抓领→掰手腕｜段02 掰开→挥拳落空→打中肩膀→撞书柜｜段03 格挡→打中胸口→逼墙角→抓领抬手｜段04 抬膝顶腹→肘击后颈→倒地→站着喘

**成片**：57.53 秒、1440×832、24fps、带音轨

### 做对的

- 抓领 + 双手扣手腕：姿势完全对
- 赵鹏把周总摁在书柜上、周总仰头闭眼：完全对
- 周总肘压后颈、赵鹏跪伏在地：完全对
- 人物脸与体型 57 秒全程一致（灰白鬓角西装 vs 微秃浅蓝衬衫）
- 场景稳定（同一间办公室，书柜/办公桌/玻璃隔断/绿植都在）

### 做错的（按严重程度）

**① 26 秒静止（最大问题）**

| 段 | 动作窗口 | 静止时长 |
|---|---|---|
| 01 | 0–7s | 7–14s（7 秒） |
| 02 | 0–8.6s | 后 4.5 秒 |
| 03 | 0–8.2s | 后 6 秒 |
| 04 | 0–5.5s | 后 9 秒 |

**② 动作降级成比划**：挥拳→抬手；打中肩膀→手碰一下；撞书柜→没撞（两人站屋子中间）；逼墙角→没逼；抓领→握手

**③ 段缝只接上一半**：段01 末帧「抓领+掰手腕」→ 段02 开头已是「分开站着」，中间「掰开」被吞

**④ 细节崩**：段01 前 1 秒周总凭空出现（跳变）；玻璃隔断反光里多出第三个人；柜子书柜/文件柜之间漂移

### 从这条片子得到的结论

- **一段 14.3 秒塞 4-5 个动作 → 只做前 2-3 个**
- **有效动作窗口 ≈ 5-7 秒**
- **57 秒的戏应拆 6-9 段，不是 4 段**

---

## 五、验收方法：联系表（contact sheet）

**为什么必须用**：单帧只能告诉你「这一帧姿势对不对」，告诉不了「他有没有在动」「动作是不是连贯」「后半段是不是僵住了」。一次只抽 4 帧就得出「全部成功」的结论，实测**结论是错的**。

### 脚本（每 0.5 秒一帧，一段一张）

```python
import cv2, numpy as np

path = r"D:/.../成片.mp4"
cap = cv2.VideoCapture(path)
fps = cap.get(cv2.CAP_PROP_FPS)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
dur = total / fps

seg = dur / 4                      # 分四段
for s in range(4):
    t0, t1 = s * seg, (s + 1) * seg
    tiles = []
    t = t0
    while t < t1:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
        ok, fr = cap.read()
        if ok:
            h, w = fr.shape[:2]
            tiles.append(cv2.resize(fr, (320, int(320 * h / w))))
        t += 0.5
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    th, tw = tiles[0].shape[:2]
    sheet = np.zeros((rows * th, cols * tw, 3), np.uint8)
    for i, tile in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r*th:(r+1)*th, c*tw:(c+1)*tw] = tile
    cv2.imwrite(rf"D:/Hermes/cache/sheet_seg{s+1}.jpg", sheet)
cap.release()
```

### 看什么

1. 哪几秒开始两个人都不动了 → 动作窗口问题（C-5）
2. 动作是不是变成比划 → 写法问题（C-1）
3. 场景有没有中途换 → Subject 引用问题（C-4）
4. 段缝接不接得上 → 段缝设计问题
5. 有没有多出来的人/手 → 反光面或贴身缠斗问题

---

## 六、sd-combat-engine 评估结论（漫剧老李套装）

**定位**：`lixiaoxiao9888-create/manju-laoli-skill` 子技能，**为 Seedance 2.5 写的**，输出七段式长句。

**可以用的（设计层）**：
- IAU 上限表：3 秒镜 ≤2 个独立动作单元，4 秒 ≤3，≥6 秒 ≤4
- 速度四拍：起（慢）→ 爆（快）→ 顿（停）→ 收（慢）
- 全身景别下限：每 2 镜至少 1 镜全身、贴脸档连续 ≤2 镜
- 双向攻防（不能一个人一直打、另一人干站）
- 自检问句：「抽掉特效能连成武打吗」
- 作者实测：3 秒塞 5 个动作只渲染第一个（这与本项目 C-1 的观察一致）

**不能用的（输出层）**：
- 顿帧 / 冲击帧三级 / 白闪 / 升格 —— **H3 一个都不执行**
- 一镜 2-3 秒写成一句长句 —— 与 H3 的分段逻辑不符

**用法**：拿它当「打斗设计手册」，输出仍按 H3 六段式 + 物理链写。

---

## 七、对照实验设计模板（以后测同类问题照抄）

凡哥的要求是「一次只变一个变量」。动作类问题的对照实验这样设计：

| 要素 | 必须锁死 |
|---|---|
| 剧情 | 完全相同的一句话 |
| 时长 / 帧数 | 相同（取 17n+5 格点，如 124 = 5.17s） |
| 参考图 | 同一批文件、同一顺序 |
| 机位 / 景别 | 同 40 度侧角、同手持锁定 |
| 风格句 | 逐字相同 |
| **唯一变量** | **写法（句式 / 详略 / 是否写物理链）** |

跑完用联系表对比，不靠单帧。
