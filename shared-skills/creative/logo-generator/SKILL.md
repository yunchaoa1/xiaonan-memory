---
name: logo-generator
description: >
  设计LOGO/品牌标志/App图标时用。Create SVG logos + high-end showcase images.
  中文触发：设计logo、做个logo、品牌标志、logo方案、出标志、品牌图标、favicon、App图标、品牌视觉。
  Generate professional SVG logos and high-end showcase images. Use when the user wants to: (1) Create a logo or icon for their product/brand, (2) Generate logo design concepts based on product information, (3) Create professional logo showcase presentations with multiple background styles, (4) Export logos in various formats (SVG, PNG), or (5) Iterate on logo designs with different visual styles. Supports geometric patterns, dot matrix designs, line systems, and mixed compositions. Generates showcase images using Nano Banana (Gemini image generation) with 12 professional background styles.
---

# Logo Generator

Generate professional SVG logos and high-end showcase presentations for products and brands.

> ⛔ **项目终止（2026-09-13）**：天使OPC数字社区 logo 项目，凡哥定论「对定稿不满意」，**已放弃由小南设计 LOGO 的方向**，不再出新一轮。本项目 8 轮迭代的核心教训（**接手同类需求前必读**）：
> ① **参照系不能由设计方自造** —— 凡哥认可的"简约大气"来自他亲自给的参照视频（BV1ka411M7kV）。方向必须由需求方给参照，不能用"我调研了趋势"替代。
> ② **缺"先圈定方向再精修"的前置门禁** —— 8 轮里反复扩大选项集（7→12→6 风格→9 组合→字母→汉字），收敛不了。下次必须先拿"一个已圈定的方向"再动笔。
> ③ **审美否决权是硬约束** —— 凡哥已否决：单色极简扁平剪影 / 具象对称翅膀 / 在字外附加元素（环、弧）。再遇品牌需求，**先问参照与主导权**，不要先出稿。
> ④ **方法沉淀依然有效**（可复用于其他品牌）：字母减法法、汉字作骨架、glitch 双色错位叠印、发光字实景合成、光学居中归一化、真透明单色公式 `alpha = 255 - min(R,G,B)`。

## Workflow

### Phase 1: Information Gathering

Collect essential information from the user:

1. **Product/Brand Name** (required)
2. **Industry/Category** (e.g., AI, fintech, design tools)
3. **Core Concept** (e.g., connection, flow, security, simplicity)
4. **Design Preferences**:
   - Style: minimal/complex, geometric/organic
   - Color preference: monochrome/specific colors
   - Mood: cold/warm, professional/friendly

Ask concise questions to gather this information. Don't overwhelm the user with too many questions at once.

### Phase 2: Pattern Matching & SVG Generation

Based on the gathered information:

1. **Generate at least 6 design variants** based on `references/design_patterns.md`
   - Match patterns to product characteristics
   - Use different pattern types and combinations for diversity
   - Include both single-pattern and mixed-pattern compositions
   - Vary complexity levels (simple geometric to layered compositions)
   - Each variant should feel distinctly different, not just parameter tweaks
   - Explain the design rationale for each variant

2. **Generate SVG code** for each variant
   - Use viewBox="0 0 100 100" for easy scaling
   - Keep code clean and well-structured
   - Use `currentColor` for flexible color control
   - Add subtle animations for web display (optional)

3. **Create interactive showcase webpage**
   - Display all 6+ logo variants in a grid layout
   - Use the template from `assets/showcase_template.html`
   - Include hover effects and smooth transitions
   - Add design rationale for each variant
   - Allow easy comparison between variants

### Phase 3: Iteration & Refinement

Allow user to provide feedback:

- Select favorite variants (narrow down from 6+ to 2-3)
- Adjust specific parameters (size, spacing, rotation)
- Combine elements from different variants
- Change colors or add gradients
- Modify animations or effects
- Generate additional variants exploring specific directions

Make targeted adjustments based on feedback. Don't regenerate everything unless requested.

### Phase 4: High-End Showcase Generation

Once the user selects a preferred logo direction:

1. **Export SVG to PNG**
   - Use `scripts/svg_to_png.py` to convert SVG to PNG
   - Default size: 1024x1024px
   - Ensure transparent background

2. **Select showcase styles**
   - Review `references/background_styles.md`
   - Recommend 4 styles based on product type and mood
   - Explain why each style fits

3. **Generate showcase images**
   - Set up environment (copy `.env.example` to `.env`, add API key)
   - Use `scripts/generate_showcase.py` with `--all-styles` flag
   - Or generate specific styles individually
   - Each image uses the PNG as reference with Nano Banana API

4. **Create final presentation webpage**
   - Combine SVG variants and showcase images
   - Use professional layout with micro-typography
   - Include download links for all assets

### Phase 5: Delivery

Provide the user with:

- Interactive HTML showcase page
- SVG files (editable vector format)
- PNG exports (various sizes if requested)
- Showcase images (4 professional backgrounds)

## Key Design Principles

1. **Provide Variety**: Generate at least 6 distinct variants to give users real choices
2. **Start Simple**: Begin with basic patterns, add complexity only when needed
3. **Meaningful Design**: Connect visual elements to product concepts
4. **Scalability**: Ensure logos work at all sizes
5. **Professional Quality**: Match high-end brand identity standards
6. **Flexibility**: Provide multiple variants for different use cases

## Technical Notes

### SVG Best Practices

- Keep viewBox at `0 0 100 100` for consistency
- Use semantic grouping with `<g>` tags
- Leverage `<defs>` for reusable elements
- Use `<clipPath>` for masking effects
- Prefer geometric primitives over complex paths when possible

### Showcase Image Generation

The `generate_showcase.py` script requires:
- Python 3.8+
- Dependencies: `pip install -r requirements.txt`
- Environment variables in `.env` file
- Reference PNG image (exported from SVG)

Supports both official Google Gemini API and third-party endpoints via `GEMINI_API_BASE_URL`.

### Available Background Styles

From `references/background_styles.md`:

**12 Professional Styles Available**:

**Dark Styles** (6):
- void (绝对虚空) - Absolute minimalism, hardcore tech
- frosted (磨砂穹顶) - Modern breathing space, premium products
- fluid (流体深渊) - AI-native fluidity, dynamic systems
- spotlight (物理影棚) - Studio lighting, editorial quality
- analog_liquid (物理流体) - Metallic shimmer on solid color base, creative brands
- led_matrix (数字硬件) - Digital retro, cyberpunk aesthetics

**Light Styles** (6):
- editorial (纸本编辑) - Specialty paper, humanistic brands
- iridescent (幻彩透砂) - Optical materials, tech hardware
- morning (晨雾光域) - AI softness, approachable products
- clinical (无菌影棚) - Spatial order, algorithm-driven brands
- ui_container (容器化界面) - Digital product native, SaaS platforms
- swiss_flat (瑞士扁平) - Absolute flatness, timeless authority

Each style has specific visual characteristics and suitable use cases. Consult the reference document for details.

## Common Patterns

### Pattern: Concentric Circle Dots
```svg
<svg viewBox="0 0 100 100">
  <g>
    <!-- Inner ring: 6 dots -->
    <circle cx="50" cy="38" r="3" fill="currentColor"/>
    <!-- Add more dots in circular arrangement -->
  </g>
</svg>
```

### Pattern: Geometric Shape with Line Accent
```svg
<svg viewBox="0 0 100 100">
  <polygon points="50,30 70,60 30,60" fill="none" stroke="currentColor" stroke-width="2"/>
  <circle cx="50" cy="30" r="4" fill="currentColor"/>
</svg>
```

### Pattern: Node Network
```svg
<svg viewBox="0 0 100 100">
  <path d="M 30 70 Q 50 70, 50 50 T 70 30" stroke="currentColor" stroke-width="2" fill="none"/>
  <circle cx="30" cy="70" r="4" fill="currentColor"/>
  <circle cx="50" cy="50" r="5" fill="currentColor"/>
  <circle cx="70" cy="30" r="4" fill="currentColor"/>
</svg>
```

For more patterns and combinations, see `references/design_patterns.md`.

## Troubleshooting

**SVG not displaying correctly**: Check viewBox and ensure all paths are closed

**PNG export fails**: Verify cairosvg is installed (`pip install cairosvg`)

**Showcase generation fails**: 
- Check `.env` file has valid `GEMINI_API_KEY`
- Verify reference PNG exists and is readable
- Check API quota/rate limits

**Third-party API not working**: Ensure `GEMINI_API_BASE_URL` is correctly formatted (e.g., `https://api.example.com/v1`)

---

## 🀄 Hermes 环境适配（小南注 · 2026-09-11）

> 原版面向 Claude Code + Gemini(Nano Banana)。装到凡哥这台机器上时按下表执行，**不要照抄原版命令**。
> 出处：https://github.com/op7418/logo-generator-skill （2,091★，作者歸藏；独立目录安装量第一）

| 原版假设 | 本环境执行方式 |
|---|---|
| `python3` 命令 | 用 `python`（本机 python3 不存在） |
| SVG→PNG 用 cairosvg | **cairosvg 在本机不可用**（缺 `libcairo-2.dll`）→ 用 **resvg-py** |
| 展示图 = Gemini Nano Banana API | 用 Hermes 原生 **`image_generate`** 工具（gpt-image-2-medium），`image_url` 传定稿 PNG 作参考 |
| `GEMINI_API_KEY` / `.env` | **不需要**；`scripts/generate_showcase.py` 本机默认不用（保留备用） |
| 输出到 `.skill-archive/` | 输出到 `D:\数字资产\图片资产\logo-<品牌名>\`（凡哥资产规范） |

### 落地流程（本机版）
1. **收需求**（Phase 1）→ 品牌名 / 行业 / 核心概念 / 风格偏好 / 主色 —— 必须问，别脑补
2. **出方案**（Phase 2）→ 依据 `references/design_patterns.md` 生成 **≥6 个**差异明显的 SVG 变体（viewBox `0 0 100 100`），每个写清设计理由；用 `assets/showcase_template.html` 拼对比页
3. **看方案** → 用 `::preview{file="..."}` 在聊天里直接看，或 `open_preview`
4. **迭代**（Phase 3）→ 凡哥挑 2-3 个方向，只调参数不重做全部
5. **定稿落地**（Phase 4）
   - SVG → PNG：`python scripts/svg_to_png.py <logo.svg> -o <logo.png> -w 1024 -H 1024`
   - 展示图：用 **`image_generate`**（`image_url`=定稿PNG），背景风格取自 `references/background_styles.md`
     · 深色系：`void` 绝对虚空 / `frosted` 磨砂穹顶 / `fluid` 流体深渊 / `spotlight` 物理影棚
     · 浅色系：`swiss_flat` 瑞士扁平 / `ui_container` 容器化界面 / `editorial` 纸本编辑
   - 纯代码质感背景：`assets/background_library.html`（WebGL）
6. **交付** → 报**路径 + 实分辨率**，SVG 原文一并给（矢量可编辑是这技能的核心价值）

### 渲染命令（实测可用）
```
pip install resvg-py          # 单文件 Rust 渲染器，无原生依赖，本机已验证
python scripts/svg_to_png.py logo.svg -o logo.png -w 1024 -H 1024
```
Chrome/Edge 亦在本机（`C:\Program Files\Google\Chrome\Application\chrome.exe`），保真度要求极高时可 `--headless --screenshot` 兜底。

### 中文字体（关键坑）
SVG 里中文必须显式指定本机已装字体，否则变豆腐块：
```
font-family="Microsoft YaHei, 微软雅黑, Source Han Sans SC, sans-serif"
```
本机 resvg-py **实测中文渲染正常**（微软雅黑可直接用）。

### 设计红线（沿用原版 design_patterns.md Part 0）
极简 / 大留白 / 比例精确 / 单焦点 / 克制不做装饰堆砌 / 缩到 16px 仍能认。

### ⚠️ 实战教训（2026-09-11 天使OPC数字社区首战 —— 必读，别再踩）
1. **动手前必须逐字读完 `references/design_patterns.md` 的 Part 0 + Part 5**，不许只看目录。首战只 grep 了目录就画，7 个方案集体违反技能明文：线宽用了 5.4–6.6（技能：≥6 即"笨重"，应用 2.5–4）；全部严格对称（技能："完美对称=无聊"）；负空间切口是尖角（技能："尖角=未完成感"）。→ 第一步永远是读 Part 0。
2. **变体按 Part 5 配额出**：纯几何 1 / 点阵 1 / 线系统 1 / 点阵×几何 1 / 线×几何 1 / 节点网络或分层 1。首战做成了"同一个创意的 7 种画法"（全是翅膀），多样性为零。
3. **单色几何图标最容易撞"素材库脸"的正是具象物**（翅膀 / 盾 / 靶心 / 维恩图 / 圆内汉堡线）。**先定审美参照**（对标品牌：腾讯云的方正几何感 / 苹果的极简 / Linear 的抽象线 / 网易的东方留白），再谈画法；**没有参照就先问凡哥，别盲画**。
4. 单色稿的"高级感"来自**比例与留白**：大胆占满画布 + 四边均匀留白（10–15 单位）+ 统一线宽，**不是靠加元素**。每稿必须缩到 16px 先看是否还成立。
5. 交付前跑 Part 4 检查表（元素 1–2 / 留白≥40% / 线宽 2.5–4 / 单一焦点 / 有意非对称 / 16px 可辨 / 无装饰）。
6. **AI 稿转"精确单色 + 真透明"后处理公式**（白底纯色稿的精确解）：`alpha = 255 - min(R,G,B)`，再整体填目标色。比"白底去背"干净，抗锯齿边缘天然正确。
7. **产出后必须自己先看**（把 PNG 拼版丢给 vision 逐个评），不许未经查看就交付。

### 🔥 活力/记忆点方向（Glitch 错位叠印）—— 2026-09-11 凡哥亲自校准
**凡哥否决了纯极简几何方向**（评语：太简单、没设计感、没高级感），给出对标物件：**抖音 logo**（活力/年轻/时尚/一眼记住）。研究后固化为可执行配方：

**依据（LogoLounge 2026 趋势报告，统计 3 万+ 标志）**
1. 年度第 1 趋势「V Balls」：由举臂/V 形围成的圆形 = 人群、团结、共享能量，**「转起来就是 community in motion」** —— 社区/平台类可直接套用。
2. 报告对 2026 的判断：**对过去十年「扁平极简、彼此长得一样」的反动**，原话「brands want to be **remembered**, not just legible」。→ **只做单色极简几何 = 撞素材库脸**，这是首战连续三轮翻车的根因。
3. 抖音手法的正式名字：**故障艺术（Glitch Art）的「错位」**。三色：青 #25F4EE + 洋红 #FE2C55 + 黑白底，**错位叠印**；符号是「音符」（取自名字的「音」）—— 关键不是抽象几何，而是**有性格的强符号**。

**配方（已实测落地）**
- **强符号 + 双色错位叠印**：一个主字形（单笔翼 / 围合环）比一堆小元素有记忆点得多。
- 错位偏移量：viewBox 100 → **5 单位**最佳。3 太含蓄看不见；>7 显脏。
- 错位层画在**底层**（先画错位色，再压主色）。
- **必须同时出单色版**（同造型去掉错位层），供印刷 / favicon / 极小程序图标兜底；深色底是这类手法的最佳舞台。
- 主色 #0052d9 配亮青 #12E2FF 实测协调（海蓝系同族，够科技活力又不脏）。

**判断标准（交付前自问）**：遮住品牌名只看符号 —— ①能不能一眼记住？②能不能一句话说出它是什么？两个都说不出 → 重做。

**流程铁律**：凡哥否决方向后，**先要到「对标参照」再动手**，不要连续盲猜。首战连猜三轮才问参照，白费三轮。

### 🏆 权威调研结论 + 面向「决策者选型」的正确流程（2026-09-11 凡哥第二轮反馈后固化）
**调研出处**：LogoLounge 2026 趋势报告（统计 30,000+ 标志，logonews.cn 有中文版）+ 全球最被记住标志榜单（Apple/Nike/Mastercard/Audi/Mercedes 等）。
**结论**：
1. 最被记住的标志共性 = **极简 + 一个有含义的故事 + 高对比 + 可缩放 + 不过时**；上榜的标志都不追潮流、不堆特效。
2. **Nike 对勾 = 胜利女神（Nike）的翅膀，同时读作「对勾=成功」** —— 一形两义是天花板手法；**翅膀本身就是世界第一标志的母题**，天使类品牌天生占优。
3. Mastercard 交叠双圆 = 连接/信任；Audi 四环 = 团结；Mercedes 三芒星 = 覆盖 —— 「关系/连接」类语义靠**几何叠合**表达最省力。
4. LogoLounge 2026 年度主题 = **动势（dynamics）**；第 1 名趋势 = **负空间里藏第二个意思**（V Balls）；另有 Little Blip：一个刻意的「歪一下」制造记忆点。
5. ⚠️ **凡哥反馈：抖音只是举例，不是必须照做**（Glitch 错位属潮流手法，与「不过时」相悖，慎用；仅在需要年轻化时作可选项）。

**面向「领导/决策者选型」的正确流程（重要）**：
- 决策者要的是**能看懂 + 有含义 + 不花哨**；抽象几何在他们眼里 = 不知道画的啥。
- 选型阶段必须给 **≥12 个不同母题**（翼/门/星/手/山/鸟/阶梯/拼图/徽章/首字母/灯塔/自然）的**具象可辨符号**。
- **一个图标一张图**，不要给同一符号的多版本（会淹没判断）；每张附星级 + 一句话含义 + 淘汰建议。
- 抽象/极简款式留到**方向定稿后**做系统化精修（那时才谈负空间、光学修正、网格对齐）。
- 生成后处理公式（白底纯色稿→精确单色+真透明）：`alpha = 255 - min(R,G,B)`，再整体填目标色，按 alpha 包围盒裁切并补 10% 留白。

### 💎 高级感的真正来源（2026-09-11 凡哥第三轮否决后固化 —— 本项目最重要的一条）
**现象**：凡哥连续否决「单色扁平极简」方向，评语：「很土」「一点高级感也没有」「像素材库」。
**根因诊断（自我复盘）**：把标志压成 *单色 + 扁平剪影 + 无材质 + 无光影 + 无字标 + 无呈现*，那就是免费 logo 生成器的脸。
**高级感不在「形状简单」，而在 材质 / 光影 / 色彩层次 / 字体气质 / 呈现方式 的合力。**

**放开后立刻见效的正确配方（已实测，凡哥评「完全不同了」）**：
1. **允许材质与光影**：玻璃质感、金属/铬、内发光、边缘光、地面反射、浮雕
2. **允许色彩层次**：深蓝→青渐变、蓝紫流体、香槟金细线、霓虹光 —— **不要限定单一色号**
3. **必须配中文字标 + 英文副标**：大字距全大写英文（`ANGEL OPC · DIGITAL COMMUNITY`）是廉价感→高级感的分水岭
4. **必须有「呈现」**：深色背景 + 柔和光晕 + 大留白构图，做成发布会/提案级的方向图
5. **一个方向 = 一张图**（同图多版本会淹没判断）；6 个方向气质要拉开（玻璃/金线/流体/霓虹/金属/3D）
**流程**：先定**气质方向** → 再定**具体图形** → 最后做**应用系统**（App图标/锁标/头图/规范）。
**技术坑**：`Source Han Serif SC Heavy` 缺 U+00B7（`·`），小标签统一用思源黑体（Noto Sans SC Medium），只有大标题才用宋体。

### 🔤 字母减法法（凡哥认可的「简约大气」思路）
出处：B站 BV1ka411M7kV《一个简约不简单的logo如何设计！》。**完整转写 + 四步法 + 歧义检查清单见 `references/字母减法法.md`**。
速记：**取一个字母骨架 → 减去一笔 → 加一点细节 → 调一下空间 → 一个字母两重含义**（特斯拉就是这么来的）。
凡哥说「简约大气」「要像视频那种思路」时 → 走这个方法，配锁标（标志+中文标准字+全大写letter-spaced英文副标），收尾用发光字实景图。

### 配合技能
- 生图风格控制：`image-prompt`、`gpt-image-style-prompting`
- 资产归档：凡哥清理铁律（换版即清旧图，别留垃圾）

