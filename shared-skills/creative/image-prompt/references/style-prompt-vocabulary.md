# 画风提示词书写方法（结构化声明 + 笔触 + 减法原则 + 精致度）

> 来源：OPC 主体资产节点多轮实测 + OpenAI GPT Image 2 官方 Cookbook + 3D 动漫漫剧领域资源（Dave 次世代CG模板 / 塔猴漫剧人物教程）。适用于 GPT Image 2；z-image 等中文工具参考「方法论」部分（中文表达画风同样要具体）。

## 核心方法论

1. **GPT Image 2 用 minimal prompting，不是关键词堆栈**：GPT Image 2 有推理层（Thinking Mode），官方明确「Precise style control with minimal prompting」。风格声明用「风格名 + 2~3 关键特征 + 1 个明确排除」，不要堆 15 个关键词（堆太多反而让模型混乱、过度执行）。
2. **结构化声明 > 逗号堆砌**：用分段标签（STYLE / OUTPUT / …）而非逗号串，风格声明放 prompt 靠前。
3. **笔触维度（画风漂移的根因）**：漂移常因"没写笔触"——模型默认走 painterly 渐变（写实）。描述**"怎么画"**比"什么风格"更能锁定画风。两条路径：平涂 cel shading（`flat color fills, hard shadow edges, no gradient brushwork`）vs painterly（`layered brushstrokes, soft painterly`）。
4. **减法原则（纠正漂移的关键，实测踩坑）**：**往动漫靠用减法，不用加法**。写实感来自 `cinematic / film-quality / real` 这些词，删掉它们就往动漫靠；硬加 anime 词（`anime lighting / anime materials / anime palette`）反而更写实。正确做法：删写实信号，保留动漫五官（`anime facial proportions with large expressive eyes`）。
5. **负向指令与正向词同等重要**：模型默认偏写实/3D，必须写 `not photorealistic / not realistic skin` 主动拉回，只写正向词拉不回来。
6. **相邻画风互漂**：3D动漫↔写实3D、日式↔韩式、水墨↔工笔，用专属词 + 负向词钉死边界。
7. **禁止品牌词**：不写 Pixar / 迪士尼 / Ghibli，直接描述视觉特征。

## 五种画风

### 1. 3D动漫电影风（真实 3D 渲染 + 动漫角色设计，非写实 Pixar、非 2D 平涂）
> 关键认知：**「3D 动漫电影」≠「三渲二」**。三渲二（cel-shaded 平涂）会漂回二次元；正确的是「真实 3D 体积 + 动漫审美」，类似《原神》/国产 3D 国漫。最终锁定声明：
```
Stylized 3D rendered anime character, next-gen 3D CG quality — 3D volume, highly detailed, rim light with warm-cool contrast, detailed skin and hair strands and fabric texture, anime facial proportions with large expressive eyes, clean bright colors; not photorealistic, not realistic skin texture, not flat 2D cel-shading.
```
避坑：禁止裸写 "3D animated film style"（漂写实）；禁止走 cel-shaded 平涂路线（漂二次元）。

### 2. 日式动漫风（2D 赛璐璐）
```
2D anime style, hand-drawn animation, cel shading, bold clean outlines, crisp linework, flat color fills, two-tone shading, expressive anime eyes, limited color palette
```
负向：`no 3D rendering, no photorealistic, no realistic skin, no smooth gradients`

### 3. 韩式彩漫/条漫风（manhwa / webtoon）
```
Korean webtoon style, manhwa style, full-color digital painting, clean smooth line art, soft cel shading, vibrant balanced color palette, detailed iris eyes, smooth skin with soft blush
```
负向：`not manga, not photorealistic`。避坑：韩式=柔和立体+全彩；日式=平涂+重线稿。

### 4. 国风水墨/工笔风
水墨（写意）：`Chinese ink wash painting, sumi-e, wet washes, dry brush, broken ink, xuan paper texture, negative space, monochrome ink, cinnabar seal stamp`
工笔（精细）：`gongbi, fine linework, layered washes, rich mineral color`
负向：`no neon colors, no glossy shading, no 3D rendering, no photorealistic`。避坑：明确 "Chinese" 区分日式。

### 5. 写实电影概念设计风
```
cinematic concept art, film concept design, real human proportions, natural materials, cinematic lighting, three-point lighting, color grading, depth of field
```
避坑：写实是默认方向，点明 "concept art / cinematic lighting" 拉电影质感而非"照片"。

## 精致度三件套（3D 动漫角色"精致感"来源）

市面 3D 动漫短剧角色精致度来自三个维度（缺一就显得廉价）：
1. **次世代 CG 质感**：`next-gen 3D CG quality`
2. **材质细节**：`detailed skin` / `hair strands` / `fabric texture`（不用泛泛的 smooth）
3. **光影强化**：`rim light`（轮廓光，人物从背景剥离）+ `warm-cool contrast`（冷暖对比）+ 体积光/丁达尔

## DERIVED_DEFAULT 精准映射（身份 → 可见细节）

身份事实推导可见细节必须**用精准词，不用模糊词**，才能让大模型发挥控制力：
- 服役复原 → `crew cut`（板寸），不是 `short hair`
- 模糊词丢失身份锚点，精准词才是控制点。上游提取可见细节、本层生成都适用。

## 使用规则

- `[STYLE]` 填结构化声明（风格名 + 关键特征 + 排除），禁止只用中文标签或笼统词，也禁止堆关键词。
- 一次一个画风，不混用。
- 人物 / 场景 / 道具共用同一套声明，保证项目视觉统一。
