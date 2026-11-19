# H3 提示词该写多长：官方 350–500 词 vs forest 的 70 词

> 2026-11-19 核查。这一条会改变所有 H3 提示词的写法，先看清来源再决定。
> 起因：凡哥问「官方指南是不是海螺平台上的 AI 说明，不是开源 H3 说明？」

---

## 一、先把来源钉死

**`ref-en.txt` 是 MiniMax 官方开源仓库的文件，不是海螺平台专属。**

```
https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt
https://huggingface.co/MiniMaxAI/MiniMax-H3/resolve/main/skills/h3-prompt-writing/references/ref-en.txt
```

**两份 sha256 完全一致：`1e574f356716ad55…`，23553 字节。** 这是官方原件。

官方 `README.zh-CN.md` 原话：
> 「该技能在 `skills/h3-prompt-writing/references/` 下提供两份提示词指南：
> `base-en.txt` 用于文本/关键帧模式，`ref-en.txt` 用于全参考（Ref2VA）模式。」

**⚠️ 第三方仓库里的同名文件可能被改过。** 本次实测 GitHub 上一个叫
`AI-KSK/aiksk-minimax-h3-local-prompt` 的仓库，它 `references/official/ref-en.txt`
是 **23894 字节**（比官方多 341 字节），哈希 `b621067b…` 对不上。
**引用「官方怎么说」之前，必须拿官方原件核哈希，别拿二手的当官方。**

---

## 二、但它的定位是「改写器输出规范」，不是「人手写说明」

文件标题就叫 **《Full-Reference Mode Rewrite Output Format Guide》** ——
**改写（Rewrite）输出格式**指南。

官方管线是三层，不是一层：

```
人写的大白话意图  →  Context-IR 改写器  →  六段式结构化提示词  →  H3 模型出片
```

**`ref-en.txt` 描述的是第二层「改写器输出」长什么样。**
而 `H3-Context-IR` 是**云端托管的预处理系统**（解析指令 → 跨模态关联 → 时间理解 → 推理 →
序列化成 H3-Base 可吃的结构），**开源权重里不含它**。

**我们本机跑 ComfyUI 走的是第三条路：手写六段式直接喂 H3，等于手工模拟改写器的产物，
但没有它的预处理能力。**

顺带说明：H3 工作流里那个 `QwenTE_ImageInfer` 节点就是在本地模拟 Context-IR。
把它绕掉之后，我们就是纯手写路线。官方对这条路的说法是：
> 「官方强烈建议接入管线，或按 Prompting Guidance **自建等价预处理**。」

也就是说手写模拟是被官方认可的，只是要自己扛住改写器本来负责的那部分细节。

---

## 三、官方对长度的原话（在第 242 行）

> **“For generation tasks, `detailed_description` is normally 350-500 English words.
> Dialogue-dense content prioritizes fitting the complete spoken timeline rather than
> mechanically reaching word count.”**

还有开篇第 7 行：

> **“Make `detailed_description` as detailed and explicit as possible. For each shot,
> clearly establish the current composition, subject appearance and position, environment
> and lighting, actions and state changes, camera movement, current sound, and the points
> where referenced content actually appears or takes effect. **Avoid reducing the description
> to a plot summary or a list of reference relationships.**”**

**官方从没说过「一镜 ≤70 词」。** 那个 70 是 `forest-laoli-h3` 的经验阈值，
不是官方规定。它的作用是「保守写法下别让 H3 丢指令」，代价是写不细。

---

## 四、官方与 forest 还有两处口径不同（知道就好，别当成谁错了）

| 项 | 官方 ref-en.txt | forest |
|---|---|---|
| 不说话的角色 | **不给 speaker ID**（只有实际发声的人才分配 `(S1)`、`(S2)`） | 写死 `silent, her lips closed` |
| 切镜条件 | **切镜必须带来真正的新信息**（新主体/空间/状态/视角/时间）；**只是构图微调就用运镜，别切** | 换嘴就切（回合制） |
| 台词密度高时 | **台词时间轴完整优先，压过词数目标** | 按词数硬卡 |

两种都能用，**冲突时以「这一镜到底要 H3 干什么」为准**，不要机械选边。

---

## 五、为什么 80 词那颗会废：不是词多，是写得粗

同一件事，两种写法差在哪：

**我们写的（80 词那颗，废了）：**
```
the other hand pushing into her shoulder
```
→ H3 只能画出「手在肩上」。往哪推？推多用力？她该有什么反应？一个字都没交代。

**官方示例的密度：**
```
her right shoulder rotates and drives one compact straight punch along a visible path
toward his upper chest
→ moves his left forearm outward to intercept it. Their arms visibly meet.
→ The redirected fist passes just outside his shoulder instead of passing through his body.
→ The short collision changes both of their upper-body angles
```
→ 轨迹、接触点、接触后果、**防穿帮（用「往外掠而不是穿过」这种正向锚定）**，全写死了。

**推论：官方那 450 词里，真正的「动作指令」也许只占 150 词，其余全是环境、衣着、相机、
防穿帮 —— 那些是约束，不抢动作的算力。**

✅ **已在 §六 用真跑验证：这个推论成立。**
**「词多会丢动作」是误判。丢动作的真实原因是动作写得模糊，不是字数超标。**
同一 5.17 秒，64 词写成静态搭肩，516 词写成了真的推。

---

## 六、判定实验：**结论 —— 长版赢，词数不是问题，写法才是**

同一剧情（他绕过桌子推开她肩膀）、同一 5.17 秒（124 帧，两颗都是 124 帧完全对齐）、
同一批参考图（s1/s2/s3）、同一机位，**只改写法**：

| | 短版 | 长版 |
|---|---|---|
| 写法 | forest：一镜 ≤70 词，只写关键点 | 官方指南：轨迹 + 接触点 + 受力反应 + 重心转移 |
| `[Shot 1]` 词数 | **64** | **516** |
| detailed_description 全段 | 78 | 539 |

### 出片对比（2026-11-19 真跑，肉眼可辨）

| 观察点 | 短版 64 词 | 长版 516 词 |
|---|---|---|
| 他的手 | 搭在肩上，像拍肩 | **按在锁骨下方，手臂伸直、身体前倾在发力** |
| 她的身体 | **直立、面上带笑** | **上身后仰，越过髋线** |
| 她的表情 | 平静 | **眼睛紧闭、眉头皱起** |
| 手脚 | 双手垂着 | **双臂张开保平衡（失重）** |
| 位置 | 没动 | **确实退开了半步**（3.6s 比 2.8s 更靠后） |

**短版出片 = 「领导拍肩安慰」。长版出片 = 「真的在推」。**

### 定论（推翻了「词多会丢动作」这个假设）

**H3 不认识「推」这个动词，只认识「手掌沿一条可见的线移动，落在锁骨下方，
压力使她的上身向后越过髋线」。它认物理，不认动词。**

所以：
- **不要再把「一镜 ≤70 词」当硬上限。** 那只是 forest 的保守经验值。
- **要管的是「动作条数」**（见 `h3-action-density-and-fight-scenes.md` 的 IAU 表），
  不是字数。一个动作写 100 词写透，比四个动作写 20 词写糊要好得多。
- **词数的正确算法：按「物理链」写，写清楚为止。** 5 秒单镜 516 词能跑通。

### 长版暴露的两个缺陷（都不是写法理论的错）

1. **场景又漂了** —— 长版正文用大白话描述环境，没把 `<Subject 3>`（办公室）写进去，
   H3 就自己编了一间房。**再次印证：正文必须引用所有用到的 `<Subject N>`。**
2. **手的位置偏高** —— 写「肩膀外缘锁骨下方」，画出来压在脖子和肩之间。
   **接触点要往低了写、具体到骨性标志**（锁骨下方 → 写「距锁骨 5 厘米、肩头外侧」更稳）。

### 可复用的「物理链」写法（这是本次真正的产出）

任何一个动作，必须写全这五段，缺一段 H3 就退化成静态姿势：

1. **出发部位** —— 手掌 / 拳头 / 膝盖 / 手肘
2. **走什么线** —— `travels along a clear, visible line`、`along a visible path`
3. **落在哪个点** —— 具体到骨性标志（锁骨下方、下巴侧面、肋骨下缘）
4. **接触后什么后果** —— 布料起皱、肌肉受压、上身越过髋线
5. **身体怎么找平衡** —— 退半步、脚跟撞椅腿、手臂张开

**外加一条防穿帮（正向写，不能写否定词）**：
`The palm does not pass through her body` → 这种「否定式」H3 会当真画出来（见 H13 词根清洗）。
正确做法是写**正向结果**：`passes just outside his shoulder`、`the fist carries past the line of his neck`。

---

## 七、顺手记下的两个操作细节

**① 手写 UI→API 转换时，`COMFY_DYNAMICCOMBO_V3` 会吃掉额外的 widget 值**

凡 `input` 里出现 `COMFY_DYNAMICCOMBO_V3`（`MiniMaxH3ReferenceSplitter.aspect_ratio`、
`MinimaxH3LatentUpscaler3D.mode`、`BlockSparseAttention.selection` 都是），
它在 `widgets_values` 里占 **不止一个槽位**，导致**后面所有参数整体前移**，
症状是「参数值跑到了隔壁参数名下」（本次见到 `end_percent = 1.3 > max 1.0`、
`precision = True not in ['fp32','fp16','bf16']`）。

- **子参数名要带点**：`mode.scale`、`aspect_ratio.size1`，不是裸 `scale`。
- **认清代价**：删掉这类节点（如两个 `BlockSparseAttention`）功能不丢，只是慢一点，
  比赌参数名靠谱得多。

**② 核验「下载的技能是不是原版」的标准动作**

```bash
# 1) 先确认分支与真实路径（文件常在仓库子目录里，如 forest-laoli-h3/forest-laoli-h3/SKILL.md）
curl -sL -x http://127.0.0.1:7897 \
  "https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1"
# 2) 逐个 sha256 对比本地与官方原件
sha256sum SKILL.md scripts/*.py references/*.md
```

**注意**：路径猜错时 `raw.githubusercontent.com` 会返回 14 字节的 `404: Not Found`，
四个文件哈希全都一样（`d5558cd4…`）就是这个现象 —— **看到相同哈希先怀疑没下到，不要以为对上了。**
