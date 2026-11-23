# 表演层 · 四区肌肉（FACS for H3）

> **为什么必须有这一层**：H3 丢弃心理词、渲染词根。"她很紧张"里的"紧张"没有可画的形状，模型只能调出通用模板——皱眉 + 瞪眼 + 抿嘴，一张表情包。
> **解法**：把情绪拆成**看得见的肌肉动作**。这不是电影学院的花活，是 H3 的语法要求。

---

## 一、四区总表

只要写四区，就能覆盖 90% 的情绪。**四区之外不必写**（写多了反而稀释）。

| 区 | 肌肉 | 可见效果（写这个） | H3 英文写法 |
|---|---|---|---|
| **眉** | 皱眉肌 | 眉心下压、眉心挤出竖纹 | `her brows pull together` / `two vertical lines appear between her brows` |
| | 额肌内侧 | 眉毛内侧上抬（委屈、悲伤） | `the inner ends of her brows lift` |
| | 额肌外侧 | 眉毛整体上抬（惊讶、疑问） | `her eyebrows rise` |
| **眼** | 眼轮匝肌 | 眼尾收缩、眼下隆起（**真笑的唯一证据**） | `the outer corners of her eyes tighten` / `the skin under her eyes bunches` |
| | 上睑提肌 | 上眼睑抬高、露出更多眼白（惊恐、瞪） | `her upper lids lift, more white showing` |
| | 眼睑下垂 | 上眼睑压低（疲惫、麻木、轻蔑） | `her lids hang low` |
| **口** | 颧大肌 | 嘴角上提（笑） | `the corners of her mouth lift` |
| | 降口角肌 | 嘴角下压（厌恶、忍住、不悦） | `the corners of her mouth pull down` |
| | 笑肌 | 嘴角横向拉开（**假笑**——只横向不带上眼） | `her mouth stretches sideways` |
| | 口轮匝肌 | 双唇压紧 / 噘起 / 分开 | `her lips press into a thin line` / `her lips part by a finger's width` |
| **颌** | 咬肌 | 腮帮鼓起、下颌咬紧 | `her jaw muscles stand out` / `her teeth are clenched` |
| | 颏肌 | 下巴上顶起皱（忍泪、强撑） | `the skin of her chin creases` |
| | 下颌下落 | 嘴微张（愣住、失神） | `her jaw goes slack` |

**四区速记**：`眉说情绪，眼说真假，口说态度，颌说力度`。

---

## 二、铁律：不写 AU 编号，不写心理词

| ❌ 不能写 | 为什么 | ✅ 改写成 |
|---|---|---|
| `AU4 + AU12` | AU 编号是内部标注，H3 不认识，会当噪声 | `her brows pull together, the corners of her mouth lift` |
| `she is nervous` | 心理词，无可画形状 | `her breathing turns shallow, her thumb presses into her index finger` |
| `she looks sad` | "sad" 是结论不是动作 | `the inner ends of her brows lift, her gaze drops to the floor` |
| `she smiles bitterly` | "bitterly" 是程度形容词 | `only the corners of her mouth lift, her eyes stay flat` |
| `she looks at him coldly` | "coldly" 无形状 | `she looks at him without blinking, her lids low` |
| `her expression is complicated` | 抽象 | 拆成两拍：先 `her brows pull together`，再 `her lips press tight` |

**判据一句话**：写完之后问自己——**这个部位在画面里能被看见在动吗？** 看不见的就是形容词。

---

## 三、幅度怎么写（H3 特有）

H3 对程度副词（`slightly` / `very` / `a little`）不敏感，容易幅度失控。**用可见计数替代**：

| ❌ 程度词 | ✅ 可见计数 |
|---|---|
| `slightly open mouth` | `her lips part by a finger's width` |
| `very tight jaw` | `her jaw muscles stand out, two ridges at the sides` |
| `a little frown` | `a single crease between her brows` |
| `eyes wide` | `more white showing above her pupils` |
| `smile a little` | `only the left corner of her mouth lifts` |
| `breathing hard` | `her shoulders rise and fall with each breath` |
| `hands shaking` | `the teacup rattles against the saucer` |

**原则**：**能量化的量化（几颗牙、几指宽、几道纹），不能量化的换成物理后果（杯子响、肩膀起伏）**。

---

## 四、景别与表演幅度绑定（写多了会被裁掉）

**景别只能写它装得下的东西**。特写里写"她后退两步"——装不下，模型要么改景别要么出怪构图。

| 景别 | 装得下 | 装不下（写了就会崩） |
|---|---|---|
| **大特写**（眼睛/嘴/手） | 眼睑、瞳孔、眼周皮肤、唇线、指尖 | 眉、下颌、肩、任何位移 |
| **特写** | 眉 + 眼 + 唇 + 下颌 + 鼻息 | 肩以下、手部动作（除非手入画） |
| **近景**（胸以上） | 上述 + 肩、颈、耳根、手的起势 | 完整手部动作、腰部以下 |
| **中景**（腰以上） | 上半身、手臂、手势、面前桌面 | 完整腿部、房间全貌 |
| **全景** | 全身、姿态、人物与空间关系 | 面部细节（会糊成一团） |
| **远景** | 空间、人数、规模 | 任何个体表情 |

**短剧实战配比**：
- **9:16 竖屏（推荐档，偏中近）**：中近景 40–50% · 特写 20–25% · 中景 15–20% · 全景 10–15% · 大特写 ≤10%
- **16:9 横屏（实测可用档）**：中近景 35–45% · 特写 25–30% · 中景 15–20% · **全景 20–30%** · 大特写 ≤10%（横屏脸像素占比小，特写要往上提）

---

## 五、四区组合的三种模式

单区只够表达一个瞬间；真正有戏的是**组合 + 时间差**。

| 模式 | 结构 | 用于 | 例子 |
|---|---|---|---|
| **同步** | 四区同时朝一个方向 | 强情绪爆发（一秒到位） | 眉压 + 眼紧 + 唇压 + 颌紧 = 愤怒 |
| **错位** | 口在笑、眼不动 | **假笑、客套、伪装**（最有戏） | `her mouth stretches sideways, the skin around her eyes stays flat` |
| **递进** | 先眉、再眼、后口 | 情绪转折（有过程才可信） | `her brows pull together` → `her eyes stop moving` → `her lips part` |

**注意**：**递进要拆镜**。H3 单镜内不做多阶段演进，串在同一句里会变成同时发生。正确做法——三个阶段各一镜，或第一镜写前两区，第二镜写后两区。

---

## 六、三条禁令

1. **不写"没有"类否定**（`her face shows no emotion` → 会被画出"表情"）→ 改 `her face stays still, her eyes fixed on the wall`
2. **不写比喻**（`like a stone` / `as if frozen`）→ 喻体会被画出来（石头、冰）
3. **写在画面段，不写进声音段**（`her voice is hoarse` 放 `overall_soundscape` 会变成环境音，放画面段会变成表情）→ 语气只在 `<d>` 后的语气位写

---

## 七、自检三问（每写一个表演句必过）

1. **看得见吗**？每个词都能在画面里指出位置吗？
2. **装得下吗**？这个动作在当前景别里能出现吗？
3. **是不是结论**？"她很委屈"是结论；"眉毛内侧上抬 + 下巴起皱"是过程。**只写过程**。

三问有一个"否"，回 `acting-recipes.md` 查对应情绪的四区配方。

---

## 八、物理链三层（一个动作写到多厚，H3 才会真的做）

> **为什么单列这一节**：前面七节解决了「写哪个部位」，没解决「写多厚」。2026-11-23 实战：200 秒成片里她的眉 0 次、眼皮 0 次——四区一个不缺，但每区只有一句话。H3 把「一句话」读成**状态**，不读成**动作**：眉毛是「抬着的」，不是「抬起来的」。
> **结论先给**：一个表演动作必须写到三层——**肌肉怎么动 → 皮肤表面出现什么 → 保持多久**。三层缺一层，这个动作就退化成一张姿势。

### 八·一 三层各写什么

| 层 | 写什么 | 词性 | 缺了会怎样 |
|---|---|---|---|
| **L1 肌肉** | 哪块肌肉、往哪个方向、幅度多少 | 动词 + 部位 | 没有动作，只有表情包 |
| **L2 表面** | 皮肤/布料上出现什么：竖纹、沟、皱、发白、鼓起、堆叠、拉扯 | **可见名词**（纹/沟/皱/白/鼓） | 有动作但没痕迹，H3 只能调通用模板 |
| **L3 保持** | 这个痕迹停在脸上几拍/几秒，**被什么打断** | 时间 + 下一个动作 | 动作一闪而过，24fps 抓不住，观众看不见 |

**L2 是全片最容易漏的一层，也是 H3 唯一认的「动作已经发生」的证据。** L1 是意图，L2 是结果，L3 是观众来得及看见的那一瞬。

### 八·二 脸部三层模板（四区都用这一套）

| 演什么 | L1 肌肉 | L2 表面痕迹 | L3 保持 |
|---|---|---|---|
| 委屈 | `the inner ends of her brows lift` | `two short vertical creases appear between her brows` | `she holds it for two beats before her brows drop back` |
| 忍泪 | `her jaw muscles tighten` | `the skin of her chin creases, two ridges stand out at the sides of her jaw` | `she keeps her jaw clenched through the next line, then swallows and it lets go` |
| 假笑 | `her mouth stretches sideways` | `the skin under her eyes stays flat, no bunching at the lower lids` | `she holds the smile until he looks away, then it drops off her face` |
| 被戳中 | `her lids hang low, her gaze drops to the table` | `a single crease deepens between her brows` | `she stays like that for three seconds, then her thumb presses into her knuckle` |
| 愣住 | `her jaw goes slack` | `her lips part by a finger's width, the lower lip hangs` | `she holds the open mouth through his whole next sentence, then swallows` |

**写法口径**：L2 一律用**能指着看的东西**（一道纹、两排骨、一指宽的缝、指节上的白），不许用形容词。躲不开否定时改成正向锚定：不写 `no bunching under her eyes` 这类孤句，写在 `the skin under her eyes stays flat` 后面（见第六节禁令 1）。

### 八·三 肢体三层 = 五段物理链的压缩版

肢体动作的三层，就是 `h3-action-density-verification-2026-11-21.md` 第三节那五段的归并：

| 三层 | 对应五段 | 写什么 |
|---|---|---|
| **L1** | ① 出发 + ② 路径 + ③ 落点 | 哪个部位出发、沿一条看得见的线、精确落到哪块骨头上 |
| **L2** | ④ 接触后果 | 受力方的几何变化 + 布料/皮肤被压出的堆叠与拉扯 |
| **L3** | ⑤ 重心与恢复 | 位移量（半步/几厘米）+ 稳身动作 + 停住几拍 |

**缺 L1=摆姿势，缺 L2=手穿过去了也没人发现，缺 L3=动作做完人就僵在那儿（实测 57 秒片子里 26 秒静止就是这么来的）。**

### 八·四 2026-11-21 实测：同一颗镜，64 词 vs 516 词

**条件全部相同**：同一段剧情（他绕过桌子推她肩膀）、5.17 秒／124 帧、同三张参考图（人物四视图 ×2 + 办公室）、同机位（40 度侧角手持锁定）、同风格句。唯一变量＝写法。

**短版（64 词，一句话式）**：

```
He rounds the desk corner toward <Subject 1> and plants one palm flat against her left shoulder.
Her shoulder is shoved back and she staggers half a step, her heel knocking the chair leg.
The desk and the chair stay where they are.
The movement stops and the picture holds still for the last second.
```

**出片结果**：手掌搭在肩上，她**笔直站着**、面带笑、双手垂着。画面读作「领导拍肩安慰」，**完全没有推力**。

**长版（516 词，三层物理链）关键段**：

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

**出片结果**：上身被推得后仰、眼睛紧闭眉头皱、双臂张开、**真的退开了半步**（3.6 秒位置明显比 2.8 秒靠后）。

**结论：同一颗镜、同一时长，516 词做的动作比 64 词多。词数不是限制器，「写没写到 L2/L3」才是。** 另有对照：14.3 秒长镜写 **760 / 836 / 759 / 797 词**，四段全部跑通、零 node_errors、八拍动作做完。

### 八·五 一句话式 vs 三层式，逐拍对照

同一个动作，两套写法摆在一起看，缺的是哪一层一目了然（全部取自上面的实测原文）：

| 拍 | 一句话式（64 词版） | 三层式（516 词版） | 缺的是 |
|---|---|---|---|
| 接触 | `plants one palm flat against her left shoulder` | `His open palm travels along a clear, visible line and lands flat on the outer edge of her left shoulder, just below the collarbone.` | L1 的**路径**：没有线，手是瞬移过去的 |
| 受力 | `Her shoulder is shoved back` | `its forward pressure drives her whole upper body backward: her left shoulder is pushed behind the line of her hips, her head tips back` | L2 的**几何**：只动肩＝局部抖一下；肩过胯线+头后仰＝整个人被推 |
| 痕迹 | （无） | `the fabric of the grey cardigan bunches and creases around his hand` | **整个 L2**：布料堆叠是「力真的传过去了」的唯一证据 |
| 位移 | `her heel knocking the chair leg` | `Her weight transfers onto her back foot. She takes half a step backward, and her heel strikes the base of the black mesh chair with a small recoil.` | L3 的**重心**：先移重心再退，才有「退」；只写脚跟碰椅子，是退完之后的事 |
| 恢复 | （无） | `Her arms swing up loosely in front of her chest as she fights for balance.` | L3 的**收**：没有恢复动作，人就是被摆过去的道具 |
| 收尾 | `The movement stops and the picture holds still for the last second.` | —（长版摘录到此处，靠重心与呼吸自然收） | 短版把「保持」写在**画面**上，长版把「保持」写在**人**身上 |

**判据**：一条 3 秒的动作，至少 3 句；**每层至少 1 句**；其中必须有一句是纯 L2（只写痕迹，不写动作）。写完数一遍——**这一镜里「皮肤或布料上留下来的东西」出现在哪句话里？** 答不上来就是写太薄了。

**同一条判据反过来用**：把 L2 那句删掉再读一遍，如果读起来还成立，说明 L1 写得太笼统（`plants one palm` 就是），得先补路径和落点。

### 八·六 什么时候该用三层，什么时候一句话就够

| 镜型 | 用几层 | 写法 | 词量参考 |
|---|---|---|---|
| **大特写**（眼睛/嘴/手）情绪镜 | 三层，但 L2 只写在**眼周、唇线、指节** | 一道纹、一排骨、一处发白，占满整镜 | 一个动作 3 句起 |
| **特写**情绪镜（裂、忍、假笑、答不上来、愣住） | **三层全写**，递进拆成两镜（第五节） | L1 一镜、L2+L3 一镜 | 一个动作 40–80 词 |
| **近景**关键动作（递东西、抓袖口、握手、擦眼泪） | 三层各一句 | L2 写布料/指节，L3 写停几拍 | 一个动作 30–50 词 |
| **中景**走位/交代（进门、坐下、转身） | **一句话就够** | 只写方向 + 结果 | 一句 15–30 词 |
| **全景 / 远景 / 过场** | **一句话** | 谁从哪到哪，不写脸 | 一句 |
| **群戏背景人** | **一句话** | 只写时间差（谁慢半拍） | 一句 |

**判据一句话：这镜的戏在脸上，就用三层；戏在空间里，一句话就够。**

两个高发误用：
- **远景写三层**——脸在画面里只有几十像素，L2 的纹和沟会被糊成一团（第四节：景别只能写它装得下的东西）。
- **特写只写一句话**——最贵的镜头配最薄的写法，就是 2026-11-23 那部片子「眉 0 次、眼皮 0 次」的直接原因。

### 八·七 三条硬规矩 + 自检三问

1. **三层缺一层，就不是动作，是姿势。** 尤其不能省 L2。
2. **L3 必须写在动作上，不能写在画面上。** ❌ `the picture holds still`（观众看到的是停摆）→ ✅ `she keeps her jaw clenched through the next line`（观众看到的是她在忍）。
3. **L2 必须装在景别里。** 大特写写「下巴起皱」会被裁掉；特写写「布料堆叠」看不见腰。写之前先问：这一层在当前景别里有没有像素。

**自检三问（每写一个表演句必过）**：

1. **皮肤上有痕迹吗**？这句里有纹、沟、皱、白、鼓、堆叠中的任何一个吗？
2. **保持了几拍**？这个痕迹被哪个下一动作打断？（答「一直保持着」＝没写 L3）
3. **删掉 L2 还成立吗**？成立 → L1 太笼统，回去补路径和落点。

三问全过，这个动作才配得上一个特写。
