---
name: h3-acting-layer
description: Use when H3 提示词的脸和声音要写出变化、或情绪爆发太突兀时。
version: 1.0.0
author: 小南
license: MIT
metadata:
  hermes:
    category: creative
    tags: [h3, acting, emotion, prompt]
---

# H3 表演层：四区肌肉 · 三拍递进 · 语调变化

## When to Use

- 用户说「人的面部表情一直没变化」「说话的节奏一直不变」「哭得太突然」「情绪太平」
- 写 H3 提示词时，需要把情绪落到具体表演
- 一段戏有情绪转折（吵架、破防、崩溃、摊牌），需要设计铺垫
- 片子机检全绿但看起来"死"的

**不适用**：只要画面不要表演的空镜／纯风光／纯动作段（那里写身体链和运镜就够）。

## 一、为什么必须分四区

**只写"眼睛动"= 脸只动了一个部位，观众看到的是"表情包"，不是"人在忍"。**

四区分工：**眉说情绪，眼说真假，口说态度，颌说力度。**

| 区 | 写法（可直接抄） |
|---|---|
| **眉** | `her brows pull together`（眉心下压）／`the inner ends of her brows lift`（眉内侧上抬=委屈/悲伤）／`her brows go flat`（麻木）／`her brows tremble`（破防前一秒） |
| **眼** | `her eyes stop blinking`（定住）／`her lids hang low`（疲惫/麻木）／`her eyes turn up, water gathers along her lower lids`（强忍眼泪）／`her eyes widen and lose focus`（失焦=裂开） |
| **口** | `her lips press into a thin line`（压住）／`her lower lip pulls inward`（忍）／`her mouth opens and her teeth show`（崩溃）／`her lips part by a finger's width`（愣住） |
| **颌** | `her jaw muscles stand out`（咬紧）／`the skin of her chin creases`（下巴起皱=忍泪）／`her jaw goes slack`（失神）／`her jaw shakes`（崩溃） |

**幅度用可见计数，不用程度词**：`lips part by a finger's width`（不是 slightly open）／`two vertical lines between her brows`（不是 a little frown）／`more white showing above her pupils`（不是 eyes wide）。

**"在忍"不靠形容词，靠一个不该出现的微动作**：吞咽、手指收紧、鼻息加重、脚后跟碾地。
`her throat moves in a swallow` 这一句比写十个"她很克制"都管用。

## 二、三拍递进（治"哭得太突然"）

**单镜只装一个状态。** 转折必须拆三镜，中间**必须插一个 1-2 秒的静止镜**——没有那一停，情绪是"跳"过去的，不是"裂开"的。

| 拍 | 内容 | 写法 |
|---|---|---|
| **第 1 拍 压住** | 四区同步绷紧 | `her brows pull together, her eyes stop blinking, her lips press into a thin line, her jaw muscles stand out` |
| **第 2 拍 错位裂开** | 假的那面先裂（只有一处失控） | `the skin around her eyes starts to shake` ／`her brows tremble` ／**到这里不许有泪** |
| **静止镜** | **1-2 秒，只写呼吸与眼神，无台词** | `her breath catches, her eyes stay on his face, her lids blink once, slowly` |
| **第 3 拍 释放** | 四区反向放开 | `the inner ends of her brows lift, her eyes squeeze shut, her mouth opens, her jaw shakes, tears run down` |

**关键比例**：从"第一次裂开"到"真正哭"，中间至少留 3-5 段、几十秒缓冲。**否则观众没有准备。**

**哭只到"漏"，不到"嚎"**：先肩膀抽但无声 → 出声音 → 停一拍 → 再起来。嚎出来就假了。

## 三、语调必须每段不同

**反面教材**：一部 200 秒的片子，20 段里有 11 段写着 `low flat voice`——**"flat"（平）是自己写进去的**，她当然从头到尾一个调。

- **每段语调描述必须换**，按该段情绪写具体的声音变化
- 可用：`voice held on one level`／`voice thinning on the numbers`／`voice that lets the last two words drop into a flat quotation`／`voice falling to the floor`／`voice that puts out one sound from the back of her throat`／`voice with the air pulled back`／`voice that breaks on the first sound`／`voice down to the air behind it`
- **同一段里两个人说话，声学必须反着写**（一低冷慢 / 一高亮快），做不到就拆段
- 自检：全片数一遍，同一短语**出现 3 次以上就算撞车**

## 四、标点 → 身体（台词不是念完，是按标点演）

| 标点 | 身体上是什么 | 写法（镜行正文，不进 `<d>`） |
|---|---|---|
| `，` | 半口气、视线可能落一下 | `she breaks off for half a breath, her eyes drop to the table` |
| `。` | 说完不立刻收表情，留一拍 | `her lips stay parted after the last word` |
| `？` | 先判要的是什么：要答案→前倾；要人认错→下巴抬 | `her chin lifts as she waits for his answer` |
| `……` | 气断在喉咙、话没说完就停 | `her breath catches, the words stop in her throat` |
| `——` | 急刹改口、肌肉先收再转 | `her mouth closes mid-word, then she starts again` |
| `（沉默）` | **不能只写"沉默"** | `she holds his eyes, her jaw tightens, then she turns her face away` |

**禁令**：不写"说到逗号时停顿"——标点是语义标记，写成时间点模型会切出怪停顿。

## 五、不说话的人怎么演（听戏五步）

**短剧里 70% 的镜头没人在说话。** 只写"看着她"等于没写。

```
① 听见（动作停住/头微转）→ ② 眼神移动（落到对方脸上并停住）→ ③ 呼吸变化（肩抬/屏住/变浅）→ ④ 身体泄漏（手指收紧/吞咽/下颌绷）→ ⑤ 余味（移开视线/呼出气）
```

**至少走三步。** 组合示例（听到坏消息）：`his hand stops over the cup` → `his eyes fix on her and stay there` → `his shoulders rise with a breath and stay up` → `his thumb presses into his knuckle until the skin whitens` → `he looks away and lets the breath out`

**典型事故**：一方说完最重的一句话，镜头切给了说话人或直接切下一段，**听的人一个反应镜都没有**——观众看不到"这句话被接住了"，后面所有情绪都无处落地。

## 六、自检三问（每句表演描述必过）

1. **看得见吗？** 每个词都能在画面里指出位置吗？（指不出=形容词）
2. **装得下吗？** 这个动作在当前景别里能出现吗？（特写里写"后退两步"必崩）
3. **是不是结论？** "她很委屈"是结论；"眉内侧上抬 + 下巴起皱"是过程。**只写过程。**

## 七、机检抓不到这个

现成机检查词根、时间戳、字数、台词密度——**它们不查"脸上有没有戏"**，因为机器判"写了错词"，判不了"什么都没写"。

「这段四区几个动作」「全片语调重不重复」必须单独查。可以写个几十行的脚本扫这两个指标，比人眼可靠。

## 相关

- 完整的 H3 格式与六段结构：`h3-video-prompt` 技能
- 30 种情绪的完整配方表、听戏五步的完整版：`forest-laoli-h3` 技能的 `references/acting-facs.md` / `acting-recipes.md` / `acting-listen.md`
- 大批量改造的分工与验收流程：`multi-agent-bulk-work` 技能
